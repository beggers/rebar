"""Benchmark harness for compile-path and Python-surface workload suites."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import pathlib
import platform
import re as cpython_re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cache
from typing import Any, Callable


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

from rebar_harness.scorecard_io import (
    build_cpython_baseline,
    build_published_subset_registry,
    build_scorecard_report_descriptor,
    load_python_dict_attribute,
    materialize_descriptor_value,
    select_published_subset_paths,
)


TARGET_CPYTHON_SERIES = "3.12.x"
REPORT_SCHEMA_VERSION = "1.0"
MANIFEST_SCHEMA_VERSION = 1
SCORECARD_REPORT = build_scorecard_report_descriptor(
    published_path=REPO_ROOT / "reports" / "benchmarks" / "latest.py",
    scorecard_kind="benchmark",
)
DEFAULT_REPORT_PATH = SCORECARD_REPORT.published_path
BENCHMARK_WORKLOADS_ROOT = REPO_ROOT / "benchmarks" / "workloads"
PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR = "published-full-suite"
BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR = "built-native-smoke"
_PUBLISHED_BENCHMARK_MANIFEST_FILENAMES = (
    "compile_matrix.py",
    "module_boundary.py",
    "pattern_boundary.py",
    "collection_replacement_boundary.py",
    "literal_flag_boundary.py",
    "grouped_named_boundary.py",
    "numbered_backreference_boundary.py",
    "grouped_segment_boundary.py",
    "literal_alternation_boundary.py",
    "grouped_alternation_boundary.py",
    "grouped_alternation_replacement_boundary.py",
    "grouped_alternation_callable_replacement_boundary.py",
    "nested_group_boundary.py",
    "nested_group_alternation_boundary.py",
    "nested_group_replacement_boundary.py",
    "nested_group_callable_replacement_boundary.py",
    "branch_local_backreference_boundary.py",
    "optional_group_boundary.py",
    "exact_repeat_quantified_group_boundary.py",
    "ranged_repeat_quantified_group_boundary.py",
    "wider_ranged_repeat_quantified_group_boundary.py",
    "open_ended_quantified_group_boundary.py",
    "quantified_alternation_boundary.py",
    "optional_group_alternation_boundary.py",
    "conditional_group_exists_boundary.py",
    "conditional_group_exists_no_else_boundary.py",
    "conditional_group_exists_empty_else_boundary.py",
    "conditional_group_exists_empty_yes_else_boundary.py",
    "conditional_group_exists_fully_empty_boundary.py",
    "regression_matrix.py",
)
_PUBLISHED_BENCHMARK_MANIFEST_MISSING_ERROR_PREFIX = (
    "unknown published benchmark manifest filename(s): "
)
_NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES = {
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR: (
        "pattern_boundary.py",
        "collection_replacement_boundary.py",
        "literal_flag_boundary.py",
    ),
}

_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR = build_published_subset_registry(
    _PUBLISHED_BENCHMARK_MANIFEST_FILENAMES,
    _NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES,
    full_suite_selector=PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    missing_filename_error_prefix=(
        _PUBLISHED_BENCHMARK_MANIFEST_MISSING_ERROR_PREFIX
    ),
)


def select_benchmark_manifest_paths(selector: str) -> tuple[pathlib.Path, ...]:
    return select_published_subset_paths(
        selector,
        filenames_by_selector=_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR,
        root=BENCHMARK_WORKLOADS_ROOT,
        unknown_selector_error_prefix="unknown benchmark manifest selector",
    )


SOURCE_TREE_SHIM_MODE = "source-tree-shim"
BUILT_NATIVE_MODE = "built-native"
NATIVE_MODULE_NAME = "rebar._rebar"


@dataclass(frozen=True)
class Workload:
    """Single benchmark workload definition."""

    manifest_id: str
    workload_id: str
    bucket: str
    family: str
    operation: str
    pattern: str
    haystack: str | None
    replacement: Any | None
    expected_exception: dict[str, Any] | None
    flags: int
    use_compiled_pattern: bool
    count: Any
    maxsplit: Any
    pos: Any | None
    endpos: Any | None
    kwargs: dict[str, Any]
    text_model: str
    haystack_text_model: str | None
    cache_mode: str
    timing_scope: str
    warmup_iterations: int
    sample_iterations: int
    timed_samples: int
    notes: list[str]
    categories: list[str]
    syntax_features: list[str]
    smoke: bool

    @classmethod
    def from_dict(
        cls,
        *,
        manifest_id: str,
        raw_workload: dict[str, Any],
        defaults: dict[str, Any],
    ) -> "Workload":
        categories = [str(category) for category in raw_workload.get("categories", [])]
        operation = str(raw_workload["operation"])
        pos = (
            None
            if raw_workload.get("pos") is None
            else normalize_numeric_workload_argument(
                raw_workload.get("pos"),
                field_name="pos",
            )
        )
        endpos = (
            None
            if raw_workload.get("endpos") is None
            else normalize_numeric_workload_argument(
                raw_workload.get("endpos"),
                field_name="endpos",
            )
        )
        use_compiled_pattern = bool(
            raw_workload.get(
                "use_compiled_pattern",
                defaults.get("use_compiled_pattern", False),
            )
        )
        expected_exception = normalize_expected_exception(
            raw_workload.get("expected_exception")
        )
        kwargs = normalize_keyword_workload_arguments(
            raw_workload.get("kwargs"),
            operation=operation,
            expected_exception=expected_exception,
            use_compiled_pattern=use_compiled_pattern,
        )
        text_model = str(raw_workload.get("text_model", "str"))
        haystack_text_model = normalize_haystack_text_model(
            raw_workload.get("haystack_text_model")
        )
        cache_mode = str(raw_workload.get("cache_mode", "cold"))
        validate_helper_keyword_argument_carriers(
            operation=operation,
            pos=pos,
            endpos=endpos,
            kwargs=kwargs,
        )
        validate_compiled_pattern_workload(
            manifest_id=manifest_id,
            operation=operation,
            pattern=str(raw_workload.get("pattern", "")),
            flags=int(raw_workload.get("flags", 0)),
            text_model=text_model,
            use_compiled_pattern=use_compiled_pattern,
            kwargs=kwargs,
            cache_mode=cache_mode,
            haystack_text_model=haystack_text_model,
            expected_exception=expected_exception,
        )
        validate_haystack_text_model_override(
            manifest_id=manifest_id,
            operation=operation,
            use_compiled_pattern=use_compiled_pattern,
            kwargs=kwargs,
            text_model=text_model,
            haystack_text_model=haystack_text_model,
            expected_exception=expected_exception,
        )
        return cls(
            manifest_id=manifest_id,
            workload_id=str(raw_workload["id"]),
            bucket=str(raw_workload.get("bucket", "unbucketed")),
            family=str(raw_workload.get("family", "parser")),
            operation=operation,
            pattern=str(raw_workload.get("pattern", "")),
            haystack=(
                None
                if raw_workload.get("haystack") is None
                else str(raw_workload.get("haystack"))
            ),
            replacement=normalize_workload_value(raw_workload.get("replacement")),
            expected_exception=expected_exception,
            flags=int(raw_workload.get("flags", 0)),
            use_compiled_pattern=use_compiled_pattern,
            count=normalize_numeric_workload_argument(
                raw_workload.get("count", 0),
                field_name="count",
            ),
            maxsplit=normalize_numeric_workload_argument(
                raw_workload.get("maxsplit", 0),
                field_name="maxsplit",
            ),
            pos=pos,
            endpos=endpos,
            kwargs=kwargs,
            text_model=text_model,
            haystack_text_model=haystack_text_model,
            cache_mode=cache_mode,
            timing_scope=str(raw_workload.get("timing_scope", "compile-path-proxy")),
            warmup_iterations=int(
                raw_workload.get("warmup_iterations", defaults.get("warmup_iterations", 2))
            ),
            sample_iterations=int(
                raw_workload.get("sample_iterations", defaults.get("sample_iterations", 1))
            ),
            timed_samples=int(raw_workload.get("timed_samples", defaults.get("timed_samples", 5))),
            notes=[str(note) for note in raw_workload.get("notes", [])],
            categories=categories,
            syntax_features=[
                str(feature)
                for feature in raw_workload.get("syntax_features", raw_workload.get("categories", []))
            ],
            smoke=bool(raw_workload.get("smoke", False) or "smoke" in categories),
        )

    def _encode_text(self, value: str, *, text_model: str | None = None) -> str | bytes:
        resolved_text_model = self.text_model if text_model is None else text_model
        if resolved_text_model == "str":
            return value
        if resolved_text_model == "bytes":
            return value.encode("utf-8")
        raise ValueError(f"unsupported text model {resolved_text_model!r}")

    def pattern_payload(self) -> str | bytes:
        return self._encode_text(self.pattern)

    def haystack_payload(self) -> str | bytes:
        if self.haystack is None:
            raise ValueError(f"workload {self.workload_id!r} requires a haystack payload")
        return self._encode_text(
            self.haystack,
            text_model=self.haystack_text_model or self.text_model,
        )

    def replacement_payload(self) -> Any:
        if self.replacement is None:
            raise ValueError(f"workload {self.workload_id!r} requires a replacement payload")
        return materialize_descriptor_value(
            self.replacement,
            text_model=self.text_model,
            callback_module_name="rebar_harness.benchmarks",
        )

    def count_argument(self) -> Any:
        return materialize_numeric_workload_argument(self.count, field_name="count")

    def maxsplit_argument(self) -> Any:
        return materialize_numeric_workload_argument(
            self.maxsplit,
            field_name="maxsplit",
        )

    def pos_argument(self) -> Any:
        if self.pos is None:
            return 0
        return materialize_numeric_workload_argument(self.pos, field_name="pos")

    def endpos_argument(self) -> Any | None:
        if self.endpos is None:
            return None
        return materialize_numeric_workload_argument(self.endpos, field_name="endpos")

    def keyword_arguments(self) -> dict[str, Any]:
        return {
            key: materialize_numeric_workload_argument(
                value,
                field_name=f"kwargs.{key}",
            )
            for key, value in self.kwargs.items()
        }


@dataclass(frozen=True, slots=True)
class BenchmarkManifest:
    """Typed benchmark manifest metadata plus typed workload records."""

    path: pathlib.Path
    manifest_id: str
    schema_version: int
    workloads: list[Workload]
    spec_refs: list[str]
    notes: list[str]

    @classmethod
    def from_dict(
        cls,
        *,
        path: pathlib.Path,
        raw_manifest: dict[str, Any],
    ) -> "BenchmarkManifest":
        schema_version = raw_manifest.get("schema_version")
        if schema_version != MANIFEST_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported benchmark manifest schema version {schema_version!r}; "
                f"expected {MANIFEST_SCHEMA_VERSION}"
            )

        defaults = raw_manifest.get("defaults", {})
        if not isinstance(defaults, dict):
            raise ValueError("benchmark manifest defaults must be an object")

        manifest_id_key = "manifest_id"
        manifest_id = str(raw_manifest[manifest_id_key])
        raw_workloads = list(raw_manifest.get("workloads", []))
        workloads = [
            Workload.from_dict(
                manifest_id=manifest_id,
                raw_workload=raw_workload,
                defaults=defaults,
            )
            for raw_workload in raw_workloads
        ]
        return cls(
            path=path,
            manifest_id=manifest_id,
            schema_version=MANIFEST_SCHEMA_VERSION,
            workloads=workloads,
            spec_refs=[str(ref) for ref in raw_manifest.get("spec_refs", [])],
            notes=[str(note) for note in raw_manifest.get("notes", [])],
        )

    def smoke_workload_ids(self) -> list[str]:
        return [
            workload.workload_id
            for workload in self.selected_workloads(selection_mode="smoke")
        ]

    def selected_workloads(
        self,
        *,
        selection_mode: str = "full",
        selected_workload_ids: tuple[str, ...] | None = None,
    ) -> list[Workload]:
        if selected_workload_ids is None:
            workloads = list(self.workloads)
        else:
            workloads_by_id = {
                workload.workload_id: workload for workload in self.workloads
            }
            workloads = []
            for workload_id in selected_workload_ids:
                if workload_id not in workloads_by_id:
                    raise AssertionError(
                        f"missing workload definition {workload_id!r} in {self.manifest_id!r}"
                    )
                workloads.append(workloads_by_id[workload_id])

        if selection_mode == "full":
            return workloads
        if selection_mode == "smoke":
            return [workload for workload in workloads if workload.smoke]
        raise AssertionError(
            f"unknown benchmark selection mode {selection_mode!r}"
        )


def normalize_workload_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [normalize_workload_value(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalize_workload_value(item_value)
            for key, item_value in value.items()
        }
    raise ValueError(f"unsupported workload value {value!r}")


def normalize_numeric_workload_argument(value: Any, *, field_name: str) -> Any:
    normalized = normalize_workload_value(value)
    if isinstance(normalized, bool):
        return normalized
    if isinstance(normalized, int):
        return normalized
    if not isinstance(normalized, dict):
        raise ValueError(
            f"benchmark workload {field_name} must be an int, bool, or "
            "indexlike descriptor"
        )

    if set(normalized) != {"type", "value"}:
        raise ValueError(
            f"benchmark workload {field_name} descriptor must contain only "
            "`type` and `value`"
        )
    if normalized.get("type") != "indexlike":
        raise ValueError(
            f"benchmark workload {field_name} descriptor only supports "
            "`type == \"indexlike\"`"
        )

    index_value = normalized.get("value")
    if isinstance(index_value, bool) or not isinstance(index_value, int):
        raise ValueError(
            f"benchmark workload {field_name} indexlike descriptor requires an "
            "integer `value`"
        )
    return {
        "type": "indexlike",
        "value": index_value,
    }


_PATTERN_HELPER_WINDOW_KEYWORD_FIELDS = frozenset({"pos", "endpos"})
_PATTERN_HELPER_WINDOW_OPERATIONS = frozenset(
    {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.findall",
        "pattern.finditer",
    }
)
_PATTERN_HELPER_KEYWORD_FIELDS_BY_OPERATION = {
    **{
        operation: _PATTERN_HELPER_WINDOW_KEYWORD_FIELDS
        for operation in _PATTERN_HELPER_WINDOW_OPERATIONS
    },
    "pattern.split": frozenset({"maxsplit"}),
    "pattern.sub": frozenset({"count"}),
    "pattern.subn": frozenset({"count"}),
}
_PATTERN_HELPER_KEYWORD_OPERATIONS = frozenset(
    _PATTERN_HELPER_KEYWORD_FIELDS_BY_OPERATION
)
_PATTERN_HELPER_EXPECTED_EXCEPTION_KEYWORD_PASSTHROUGH_OPERATIONS = frozenset(
    {"pattern.split", "pattern.sub", "pattern.subn"}
)
_PATTERN_HELPER_DUPLICATE_KEYWORD_POSITIONAL_LIMITS = {
    "pattern.split": 2,
    "pattern.sub": 3,
    "pattern.subn": 3,
}
_PATTERN_HELPER_KEYWORD_OPERATIONS_DESCRIPTION = (
    "pattern.search, pattern.match, pattern.fullmatch, pattern.findall, "
    "pattern.finditer, pattern.split, pattern.sub, and pattern.subn"
)
_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_FIELDS = frozenset({"flags"})
_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_PATTERN = "abc"
_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_PATTERN = "(?P<word>abc)"
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE = int(cpython_re.IGNORECASE)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION = {
    "type": "ValueError",
    "message_substring": "cannot process flags argument with a compiled pattern",
}
_MODULE_HELPER_KEYWORD_FIELDS_BY_OPERATION = {
    "module.search": frozenset({"flags"}),
    "module.match": frozenset({"flags"}),
    "module.fullmatch": frozenset({"flags"}),
    "module.split": frozenset({"maxsplit"}),
    "module.sub": frozenset({"count"}),
    "module.subn": frozenset({"count"}),
}
_MODULE_HELPER_KEYWORD_OPERATIONS = frozenset(
    _MODULE_HELPER_KEYWORD_FIELDS_BY_OPERATION
)
_MODULE_HELPER_EXPECTED_EXCEPTION_KEYWORD_PASSTHROUGH_OPERATIONS = frozenset(
    {"module.fullmatch", "module.split", "module.sub", "module.subn"}
)
_MODULE_HELPER_DUPLICATE_KEYWORD_FIELDS_BY_OPERATION = {
    "module.search": "flags",
    "module.split": "maxsplit",
    "module.sub": "count",
    "module.subn": "count",
}
_COMPILED_PATTERN_COLLECTION_REPLACEMENT_OPERATIONS = frozenset(
    {
        "module.split",
        "module.findall",
        "module.finditer",
        "module.sub",
        "module.subn",
    }
)
_COLLECTION_REPLACEMENT_PATTERN_WRONG_TEXT_MODEL_OPERATIONS = frozenset(
    {"pattern.split", "pattern.sub", "pattern.subn"}
)
_COMPILED_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OPERATIONS = frozenset(
    {"module.search", "module.match", "module.fullmatch"}
)
_COMPILED_PATTERN_MODULE_COMPILE_OPERATIONS = frozenset({"module.compile"})
_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS = frozenset(
    _COMPILED_PATTERN_COLLECTION_REPLACEMENT_OPERATIONS
    | _COMPILED_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OPERATIONS
)
_COMPILED_PATTERN_MODULE_OPERATIONS = frozenset(
    _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
    | _COMPILED_PATTERN_MODULE_COMPILE_OPERATIONS
)
_HELPER_KEYWORD_FIELDS_BY_OPERATION = {
    **_PATTERN_HELPER_KEYWORD_FIELDS_BY_OPERATION,
    **_MODULE_HELPER_KEYWORD_FIELDS_BY_OPERATION,
}
_HELPER_KEYWORD_OPERATIONS_DESCRIPTION = (
    "pattern.search, pattern.match, pattern.fullmatch, pattern.findall, "
    "pattern.finditer, pattern.split, pattern.sub, pattern.subn, "
    "module.search, module.match, module.fullmatch, module.split, "
    "module.sub, and module.subn"
)


def normalize_keyword_workload_arguments(
    value: Any,
    *,
    operation: str,
    expected_exception: dict[str, Any] | None = None,
    use_compiled_pattern: bool = False,
) -> dict[str, Any]:
    if value is None:
        return {}

    normalized = normalize_workload_value(value)
    if not isinstance(normalized, dict):
        raise ValueError("benchmark workload kwargs must be an object")

    if operation == "module.compile" and use_compiled_pattern:
        allowed_keys = _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_FIELDS
    else:
        allowed_keys = _HELPER_KEYWORD_FIELDS_BY_OPERATION.get(operation)
    if allowed_keys is None:
        raise ValueError(
            "benchmark workload kwargs are only supported for "
            f"{_HELPER_KEYWORD_OPERATIONS_DESCRIPTION}"
        )

    unknown_keys = sorted(
        key
        for key in normalized
        if key not in allowed_keys
    )
    if unknown_keys:
        if (
            expected_exception is not None
            and (
                operation
                in _MODULE_HELPER_EXPECTED_EXCEPTION_KEYWORD_PASSTHROUGH_OPERATIONS
                or operation
                in _PATTERN_HELPER_EXPECTED_EXCEPTION_KEYWORD_PASSTHROUGH_OPERATIONS
            )
        ):
            return {
                key: normalize_numeric_workload_argument(
                    normalized[key],
                    field_name=f"kwargs.{key}",
                )
                for key in sorted(normalized)
            }
        allowed_key_description = ", ".join(f"`{key}`" for key in sorted(allowed_keys))
        if len(allowed_keys) > 1:
            allowed_key_description = allowed_key_description.replace(
                ", ",
                " and ",
                len(allowed_keys) - 1,
            )
        raise ValueError(
            f"benchmark workload kwargs for {operation} only supports the "
            f"{allowed_key_description} key"
            f"{'' if len(allowed_keys) == 1 else 's'}; got unsupported keys "
            f"{unknown_keys!r}"
        )

    return {
        key: normalize_numeric_workload_argument(
            normalized[key],
            field_name=f"kwargs.{key}",
        )
        for key in sorted(normalized)
    }


def validate_helper_keyword_argument_carriers(
    *,
    operation: str,
    pos: Any | None,
    endpos: Any | None,
    kwargs: dict[str, Any],
) -> None:
    if not kwargs:
        return

    if (
        _HELPER_KEYWORD_FIELDS_BY_OPERATION.get(operation)
        == _PATTERN_HELPER_WINDOW_KEYWORD_FIELDS
        and (pos is not None or endpos is not None)
    ):
        raise ValueError(
            "benchmark workload cannot mix top-level pos/endpos fields with "
            "keyword kwargs carriers"
        )


def validate_compiled_pattern_workload(
    *,
    manifest_id: str,
    operation: str,
    pattern: str,
    flags: int,
    text_model: str,
    use_compiled_pattern: bool,
    kwargs: dict[str, Any],
    cache_mode: str,
    haystack_text_model: str | None,
    expected_exception: dict[str, Any] | None,
) -> None:
    if not use_compiled_pattern:
        return

    if operation not in _COMPILED_PATTERN_MODULE_OPERATIONS:
        allowed_operations = ", ".join(sorted(_COMPILED_PATTERN_MODULE_OPERATIONS))
        raise ValueError(
            "benchmark compiled-pattern module-helper workloads currently only "
            f"support {allowed_operations}; got {operation!r}"
        )

    if operation == "module.compile":
        keyword_flags = kwargs.get("flags") if kwargs else None
        supports_int_zero_keyword = (
            type(keyword_flags) is int and keyword_flags == 0
        )
        supports_bool_false_keyword = (
            type(keyword_flags) is bool and keyword_flags is False
        )
        supports_zero_or_false_keyword = (
            supports_int_zero_keyword
            or supports_bool_false_keyword
        )
        supports_ignorecase_rejection = (
            type(keyword_flags) is int
            and keyword_flags == _COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE
            and expected_exception == _COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION
        )
        if manifest_id != "module-boundary":
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads are only supported on the "
                "`module-boundary` manifest"
            )
        if kwargs and (
            set(kwargs) != _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_FIELDS
            or not (
                supports_zero_or_false_keyword
                or supports_ignorecase_rejection
            )
        ):
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `flags=0`, `flags=False`, and "
                "`flags=IGNORECASE` rejection keyword carriers"
            )
        if haystack_text_model is not None:
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "successful same-text-model literal or named-group rows or "
                "the bounded `flags=IGNORECASE` rejection rows"
            )
        if expected_exception is not None and not supports_ignorecase_rejection:
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "successful same-text-model literal or named-group rows or "
                "the bounded `flags=IGNORECASE` rejection rows"
            )
        if kwargs:
            supports_literal_keyword_success = (
                pattern == _COMPILED_PATTERN_MODULE_COMPILE_LITERAL_PATTERN
                and flags == 0
                and text_model in {"str", "bytes"}
                and supports_zero_or_false_keyword
                and expected_exception is None
            )
            supports_named_group_int_zero_keyword_success = (
                pattern == _COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_PATTERN
                and flags == 0
                and text_model in {"str", "bytes"}
                and supports_int_zero_keyword
                and expected_exception is None
            )
            supports_named_group_bool_false_keyword_success = (
                pattern == _COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_PATTERN
                and flags == 0
                and text_model in {"str", "bytes"}
                and supports_bool_false_keyword
                and expected_exception is None
            )
            if (
                not supports_literal_keyword_success
                and not supports_named_group_int_zero_keyword_success
                and not supports_named_group_bool_false_keyword_success
                and not supports_ignorecase_rejection
            ):
                raise ValueError(
                    "benchmark compiled-pattern module-helper "
                    "module.compile workloads currently only support "
                    "the bounded `abc` str/bytes literal keyword carriers, "
                    "the exact same-text-model `(?P<word>abc)` str/bytes "
                    "`flags=0` and `flags=False` named-group keyword carriers, and "
                    "`flags=IGNORECASE` rejection pairs"
                )
        elif (
            pattern
            not in {
                _COMPILED_PATTERN_MODULE_COMPILE_LITERAL_PATTERN,
                _COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_PATTERN,
            }
            or flags != 0
            or text_model not in {"str", "bytes"}
        ):
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            )

    if operation in _COMPILED_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OPERATIONS:
        if manifest_id != "module-boundary":
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads are only supported on the "
                "`module-boundary` manifest"
            )
        if kwargs:
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads currently only support "
                "positional helper calls"
            )
        if haystack_text_model is None:
            if expected_exception is not None:
                raise ValueError(
                    "benchmark compiled-pattern module-helper "
                    "search/match/fullmatch workloads currently only support "
                    "successful same-text-model rows or timed wrong-text-model "
                    "TypeError rows"
                )
        elif (
            expected_exception is None
            or expected_exception.get("type") != "TypeError"
        ):
            raise ValueError(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads currently only support "
                "successful same-text-model rows or timed wrong-text-model "
                "TypeError rows"
            )

    if cache_mode not in {"warm", "purged"}:
        raise ValueError(
            "benchmark compiled-pattern module-helper workloads currently require "
            "`cache_mode` to be `warm` or `purged` so timed callbacks exclude "
            "pattern compilation"
        )


def normalize_haystack_text_model(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value)
    if normalized not in {"str", "bytes"}:
        raise ValueError(
            "benchmark workload haystack_text_model must be `str` or `bytes`; "
            f"got {normalized!r}"
        )
    return normalized


def validate_haystack_text_model_override(
    *,
    manifest_id: str,
    operation: str,
    use_compiled_pattern: bool,
    kwargs: dict[str, Any],
    text_model: str,
    haystack_text_model: str | None,
    expected_exception: dict[str, Any] | None,
) -> None:
    if haystack_text_model is None:
        return

    if manifest_id not in {"collection-replacement-boundary", "module-boundary"}:
        raise ValueError(
            "benchmark workload haystack_text_model is only supported on the "
            "`collection-replacement-boundary` manifest and the bounded "
            "`module-boundary` compiled-pattern wrong-text-model trio"
        )

    if manifest_id == "collection-replacement-boundary":
        if operation.startswith("module."):
            operation_description = (
                "compiled-pattern module.split/module.findall/module.finditer/"
                "module.sub/module.subn workloads"
            )
            supports_operation = (
                use_compiled_pattern
                and operation in _COMPILED_PATTERN_COLLECTION_REPLACEMENT_OPERATIONS
            )
        else:
            operation_description = (
                "direct Pattern.split()/Pattern.sub()/Pattern.subn() positional "
                "helper workloads"
            )
            supports_operation = (
                not use_compiled_pattern
                and not kwargs
                and operation
                in _COLLECTION_REPLACEMENT_PATTERN_WRONG_TEXT_MODEL_OPERATIONS
            )
    else:
        operation_description = (
            "compiled-pattern module.search/module.match/module.fullmatch "
            "workloads on the `module-boundary` manifest"
        )
        supports_operation = (
            use_compiled_pattern
            and operation in _COMPILED_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OPERATIONS
        )

    if not supports_operation:
        raise ValueError(
            "benchmark workload haystack_text_model currently only supports "
            f"{operation_description}"
        )

    if haystack_text_model == text_model:
        raise ValueError(
            "benchmark workload haystack_text_model must differ from the "
            "workload text_model"
        )

    if expected_exception is None or expected_exception.get("type") != "TypeError":
        raise ValueError(
            "benchmark workload haystack_text_model currently only supports "
            "timed TypeError rows"
        )


def materialize_numeric_workload_argument(value: Any, *, field_name: str) -> Any:
    normalized = normalize_numeric_workload_argument(value, field_name=field_name)
    return materialize_descriptor_value(normalized)


def _expected_duplicate_module_helper_keyword_field(
    workload: Workload,
) -> str | None:
    expected_exception = workload.expected_exception
    expected_field = _MODULE_HELPER_DUPLICATE_KEYWORD_FIELDS_BY_OPERATION.get(
        workload.operation
    )
    if (
        expected_exception is None
        or expected_field is None
        or expected_exception.get("type") != "TypeError"
        or expected_field not in workload.kwargs
    ):
        return None
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return None
    if (
        isinstance(message_substring, str)
        and f"multiple values for argument '{expected_field}'" in message_substring
    ):
        return expected_field
    return None


def _expected_duplicate_pattern_helper_keyword_field(
    workload: Workload,
) -> str | None:
    expected_exception = workload.expected_exception
    allowed_fields = _PATTERN_HELPER_KEYWORD_FIELDS_BY_OPERATION.get(workload.operation)
    if (
        expected_exception is None
        or expected_exception.get("type") != "TypeError"
        or allowed_fields is None
    ):
        return None
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return None

    for allowed_field in allowed_fields:
        if (
            allowed_field in workload.kwargs
            and f"multiple values for argument '{allowed_field}'" in message_substring
        ):
            return allowed_field

    positional_limit = _PATTERN_HELPER_DUPLICATE_KEYWORD_POSITIONAL_LIMITS.get(
        workload.operation
    )
    if positional_limit is None:
        return None

    expected_field = {
        "pattern.split": "maxsplit",
        "pattern.sub": "count",
        "pattern.subn": "count",
    }[workload.operation]
    if expected_field not in workload.kwargs:
        return None

    helper_name = workload.operation.removeprefix("pattern.")
    bound_method_message = (
        f"{helper_name}() takes at most {positional_limit} arguments "
        f"({positional_limit + 1} given)"
    )
    if bound_method_message in message_substring:
        return expected_field
    return None


def normalize_expected_exception(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None

    normalized = normalize_workload_value(value)
    if not isinstance(normalized, dict):
        raise ValueError("benchmark workload expected_exception must be an object")

    unknown_keys = set(normalized) - {"message_substring", "type"}
    if unknown_keys:
        raise ValueError(
            "benchmark workload expected_exception contains unsupported keys: "
            f"{sorted(unknown_keys)}"
        )

    expected_type = normalized.get("type")
    if expected_type is None:
        raise ValueError("benchmark workload expected_exception requires a `type`")

    result = {"type": str(expected_type)}
    message_substring = normalized.get("message_substring")
    if message_substring is not None:
        result["message_substring"] = str(message_substring)
    return result


@dataclass
class BenchmarkRunContext:
    """Resolved benchmark execution mode plus adapter/runtime metadata."""

    requested_mode: str
    resolved_mode: str
    baseline_adapter: "BenchmarkAdapter"
    implementation_adapter: "BenchmarkAdapter"
    implementation_metadata: dict[str, Any]
    execution_model: str
    cleanup: Callable[[], None]


class NativeBenchmarkProvisionError(RuntimeError):
    """Raised when a strict built-native benchmark run cannot provision a native wheel."""


def workload_to_payload(workload: Workload) -> dict[str, Any]:
    payload = {
        "manifest_id": workload.manifest_id,
        "workload_id": workload.workload_id,
        "bucket": workload.bucket,
        "family": workload.family,
        "operation": workload.operation,
        "pattern": workload.pattern,
        "haystack": workload.haystack,
        "replacement": workload.replacement,
        "expected_exception": workload.expected_exception,
        "flags": workload.flags,
        "count": workload.count,
        "maxsplit": workload.maxsplit,
        "text_model": workload.text_model,
        "cache_mode": workload.cache_mode,
        "timing_scope": workload.timing_scope,
        "warmup_iterations": workload.warmup_iterations,
        "sample_iterations": workload.sample_iterations,
        "timed_samples": workload.timed_samples,
        "notes": list(workload.notes),
        "categories": list(workload.categories),
        "syntax_features": list(workload.syntax_features),
        "smoke": workload.smoke,
    }
    if workload.pos is not None:
        payload["pos"] = workload.pos
    if workload.endpos is not None:
        payload["endpos"] = workload.endpos
    if workload.kwargs:
        payload["kwargs"] = dict(workload.kwargs)
    if workload.use_compiled_pattern:
        payload["use_compiled_pattern"] = True
    if workload.haystack_text_model is not None:
        payload["haystack_text_model"] = workload.haystack_text_model
    return payload


def workload_from_payload(payload: dict[str, Any]) -> Workload:
    raw_workload: dict[str, Any] = {
        "id": payload["workload_id"],
        "bucket": payload["bucket"],
        "family": payload["family"],
        "operation": payload["operation"],
        "pattern": payload.get("pattern", ""),
        "haystack": payload.get("haystack"),
        "replacement": payload.get("replacement"),
        "expected_exception": payload.get("expected_exception"),
        "flags": payload.get("flags", 0),
        "count": payload.get("count", 0),
        "maxsplit": payload.get("maxsplit", 0),
        "text_model": payload["text_model"],
        "cache_mode": payload["cache_mode"],
        "timing_scope": payload["timing_scope"],
        "warmup_iterations": payload["warmup_iterations"],
        "sample_iterations": payload["sample_iterations"],
        "timed_samples": payload["timed_samples"],
        "notes": payload.get("notes", []),
        "categories": payload.get("categories", []),
        "syntax_features": payload.get("syntax_features", []),
        "smoke": payload.get("smoke", False),
    }
    if payload.get("pos") is not None:
        raw_workload["pos"] = payload["pos"]
    if payload.get("endpos") is not None:
        raw_workload["endpos"] = payload["endpos"]
    if "kwargs" in payload:
        raw_workload["kwargs"] = payload["kwargs"]
    if payload.get("use_compiled_pattern", False):
        raw_workload["use_compiled_pattern"] = True
    if payload.get("haystack_text_model") is not None:
        raw_workload["haystack_text_model"] = payload["haystack_text_model"]
    return Workload.from_dict(
        manifest_id=str(payload["manifest_id"]),
        raw_workload=raw_workload,
        defaults={},
    )


def load_manifest(path: pathlib.Path) -> BenchmarkManifest:
    if path.suffix != ".py":
        raise ValueError(
            f"unsupported benchmark manifest extension {path.suffix!r} for {path}"
        )
    raw_manifest = load_python_dict_attribute(
        path,
        module_name_prefix="_rebar_benchmark_manifest",
        attribute_name="MANIFEST",
        load_error_label="Python benchmark manifest",
        missing_error_label="Python benchmark manifest module",
        type_error_label="benchmark manifest",
    )
    return BenchmarkManifest.from_dict(path=path, raw_manifest=raw_manifest)


def load_manifests(paths: list[pathlib.Path]) -> list[BenchmarkManifest]:
    manifests: list[BenchmarkManifest] = []
    manifest_ids: set[str] = set()
    workload_ids: set[str] = set()

    for path in paths:
        manifest = load_manifest(path)
        manifest_id = manifest.manifest_id
        if manifest_id in manifest_ids:
            raise ValueError(f"duplicate benchmark manifest id {manifest_id!r}")
        manifest_ids.add(manifest_id)

        for workload in manifest.workloads:
            if workload.workload_id in workload_ids:
                raise ValueError(f"duplicate benchmark workload id {workload.workload_id!r}")
            workload_ids.add(workload.workload_id)

        manifests.append(manifest)

    return manifests


@cache
def published_benchmark_manifests() -> tuple[BenchmarkManifest, ...]:
    return tuple(
        load_manifests(
            list(select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR))
        )
    )


def select_workloads(workloads: list[Workload], *, smoke_only: bool) -> list[Workload]:
    if not smoke_only:
        return workloads

    selected_workloads = [workload for workload in workloads if workload.smoke]
    if not selected_workloads:
        raise ValueError("no smoke-tagged workloads matched the selected benchmark manifests")
    return selected_workloads


class BenchmarkAdapter:
    """Adapter boundary for benchmarkable workloads."""

    adapter_name: str
    import_name: str
    module: Any

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        raise NotImplementedError


def _clear_module(module_name: str) -> None:
    module_prefix = f"{module_name}."
    loaded_names = [
        name for name in sys.modules if name == module_name or name.startswith(module_prefix)
    ]
    for name in loaded_names:
        sys.modules.pop(name, None)
    importlib.invalidate_caches()


def import_callable(module_name: str, workload: Workload) -> Any:
    if workload.operation != "import":
        raise ValueError(f"unsupported import workload operation {workload.operation!r}")

    if workload.cache_mode in {"cold", "purged"}:

        def run_once() -> object:
            _clear_module(module_name)
            return importlib.import_module(module_name)

        return run_once

    if workload.cache_mode == "warm":
        importlib.import_module(module_name)

        def run_once() -> object:
            return importlib.import_module(module_name)

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def compile_callable(module: Any, workload: Workload) -> Any:
    pattern = workload.pattern_payload()
    uses_keyword_arguments = bool(workload.kwargs)

    if workload.operation not in {"compile", "module.compile"}:
        raise ValueError(f"unsupported compile workload operation {workload.operation!r}")

    def keyword_call_kwargs() -> dict[str, Any]:
        if not uses_keyword_arguments:
            return {}
        return workload.keyword_arguments()

    if workload.use_compiled_pattern:
        if workload.operation != "module.compile":
            raise ValueError(
                "compiled-pattern compile workloads currently only support "
                "`module.compile`"
            )
        compiled_pattern = module.compile(pattern, workload.flags)

        def invoke_compiled_pattern() -> object:
            if uses_keyword_arguments:
                return module.compile(compiled_pattern, **keyword_call_kwargs())
            return module.compile(compiled_pattern, workload.flags)

        if workload.cache_mode == "warm":

            def run_once() -> object:
                return invoke_compiled_pattern()

            return run_once

        if workload.cache_mode == "purged":
            if hasattr(module, "purge"):
                module.purge()

            def run_once() -> object:
                return invoke_compiled_pattern()

            return run_once

        raise ValueError(
            "unsupported cache mode for compiled-pattern module.compile workload "
            f"{workload.cache_mode!r}"
        )

    if workload.cache_mode == "cold":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            return module.compile(pattern, workload.flags)

        return run_once

    if workload.cache_mode == "warm":
        module.compile(pattern, workload.flags)

        def run_once() -> object:
            return module.compile(pattern, workload.flags)

        return run_once

    if workload.cache_mode == "purged":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            result = module.compile(pattern, workload.flags)
            if hasattr(module, "purge"):
                module.purge()
            return result

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def helper_callable(module: Any, workload: Workload) -> Any:
    pattern = workload.pattern_payload()
    haystack = workload.haystack_payload()
    uses_keyword_arguments = bool(workload.kwargs)
    uses_compiled_pattern = workload.use_compiled_pattern
    duplicate_keyword_field = _expected_duplicate_module_helper_keyword_field(
        workload
    )

    def compile_pattern() -> Any:
        return module.compile(pattern, workload.flags)

    def keyword_call_kwargs() -> dict[str, Any]:
        if not uses_keyword_arguments:
            return {}
        return workload.keyword_arguments()

    def invoke(compiled_pattern: Any | None = None) -> object:
        pattern_argument = (
            compiled_pattern if uses_compiled_pattern else pattern
        )
        helper_flags = 0 if uses_compiled_pattern else workload.flags
        if (
            uses_keyword_arguments
            and workload.operation not in _MODULE_HELPER_KEYWORD_OPERATIONS
        ):
            raise ValueError(
                "benchmark workload kwargs are only supported for "
                f"{_HELPER_KEYWORD_OPERATIONS_DESCRIPTION}"
            )
        if workload.operation == "module.search":
            if uses_keyword_arguments:
                if (
                    workload.flags != 0
                    and duplicate_keyword_field != "flags"
                ):
                    raise ValueError(
                        "benchmark workload module.search keyword flags carriers "
                        "currently require `flags == 0`"
                    )
                if duplicate_keyword_field == "flags":
                    return module.search(
                        pattern_argument,
                        haystack,
                        workload.flags,
                        **keyword_call_kwargs(),
                    )
                return module.search(
                    pattern_argument,
                    haystack,
                    **keyword_call_kwargs(),
                )
            return module.search(pattern_argument, haystack, helper_flags)
        if workload.operation == "module.match":
            if uses_keyword_arguments:
                if workload.flags != 0:
                    raise ValueError(
                        "benchmark workload module.match keyword flags carriers "
                        "currently require `flags == 0`"
                    )
                return module.match(
                    pattern_argument,
                    haystack,
                    **keyword_call_kwargs(),
                )
            return module.match(pattern_argument, haystack, helper_flags)
        if workload.operation == "module.fullmatch":
            if uses_keyword_arguments:
                if workload.flags != 0:
                    raise ValueError(
                        "benchmark workload module.fullmatch keyword flags carriers "
                        "currently require `flags == 0`"
                    )
                return module.fullmatch(
                    pattern_argument,
                    haystack,
                    **keyword_call_kwargs(),
                )
            return module.fullmatch(pattern_argument, haystack, helper_flags)
        if workload.operation == "module.split":
            if uses_keyword_arguments:
                if workload.flags != 0 and not uses_compiled_pattern:
                    raise ValueError(
                        "benchmark workload module.split keyword maxsplit carriers "
                        "currently require `flags == 0`"
                    )
                if duplicate_keyword_field == "maxsplit":
                    return module.split(
                        pattern_argument,
                        haystack,
                        workload.maxsplit_argument(),
                        **keyword_call_kwargs(),
                    )
                return module.split(
                    pattern_argument,
                    haystack,
                    **keyword_call_kwargs(),
                )
            if uses_compiled_pattern:
                return module.split(
                    pattern_argument,
                    haystack,
                    workload.maxsplit_argument(),
                )
            return module.split(
                pattern_argument,
                haystack,
                workload.maxsplit_argument(),
                workload.flags,
            )
        if workload.operation == "module.findall":
            return module.findall(pattern_argument, haystack, workload.flags)
        if workload.operation == "module.finditer":
            return list(module.finditer(pattern_argument, haystack, workload.flags))
        if workload.operation == "module.sub":
            if uses_keyword_arguments:
                if workload.flags != 0 and not uses_compiled_pattern:
                    raise ValueError(
                        "benchmark workload module.sub keyword count carriers "
                        "currently require `flags == 0`"
                    )
                if duplicate_keyword_field == "count":
                    return module.sub(
                        pattern_argument,
                        workload.replacement_payload(),
                        haystack,
                        workload.count_argument(),
                        **keyword_call_kwargs(),
                    )
                return module.sub(
                    pattern_argument,
                    workload.replacement_payload(),
                    haystack,
                    **keyword_call_kwargs(),
                )
            if uses_compiled_pattern:
                return module.sub(
                    pattern_argument,
                    workload.replacement_payload(),
                    haystack,
                    workload.count_argument(),
                )
            return module.sub(
                pattern_argument,
                workload.replacement_payload(),
                haystack,
                workload.count_argument(),
                workload.flags,
            )
        if workload.operation == "module.subn":
            if uses_keyword_arguments:
                if workload.flags != 0 and not uses_compiled_pattern:
                    raise ValueError(
                        "benchmark workload module.subn keyword count carriers "
                        "currently require `flags == 0`"
                    )
                if duplicate_keyword_field == "count":
                    return module.subn(
                        pattern_argument,
                        workload.replacement_payload(),
                        haystack,
                        workload.count_argument(),
                        **keyword_call_kwargs(),
                    )
                return module.subn(
                    pattern_argument,
                    workload.replacement_payload(),
                    haystack,
                    **keyword_call_kwargs(),
                )
            if uses_compiled_pattern:
                return module.subn(
                    pattern_argument,
                    workload.replacement_payload(),
                    haystack,
                    workload.count_argument(),
                )
            return module.subn(
                pattern_argument,
                workload.replacement_payload(),
                haystack,
                workload.count_argument(),
                workload.flags,
            )
        raise ValueError(f"unsupported module helper operation {workload.operation!r}")

    if uses_compiled_pattern:
        compiled = compile_pattern()

        if workload.cache_mode == "warm":

            def run_once() -> object:
                return invoke(compiled)

            return run_once

        if workload.cache_mode == "purged":
            if hasattr(module, "purge"):
                module.purge()

            def run_once() -> object:
                return invoke(compiled)

            return run_once

        raise ValueError(
            "unsupported cache mode for compiled-pattern module helper "
            f"{workload.cache_mode!r}"
        )

    if workload.cache_mode == "cold":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            return invoke()

        return run_once

    if workload.cache_mode == "warm":
        if workload.expected_exception is None:
            invoke()
        else:
            module.compile(pattern, workload.flags)

        def run_once() -> object:
            return invoke()

        return run_once

    if workload.cache_mode == "purged":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            result = invoke()
            if hasattr(module, "purge"):
                module.purge()
            return result

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def pattern_helper_callable(module: Any, workload: Workload) -> Any:
    pattern = workload.pattern_payload()
    static_haystack = (
        None
        if workload.haystack_text_model is not None
        else workload.haystack_payload()
    )
    uses_positional_window = workload.pos is not None or workload.endpos is not None
    uses_keyword_arguments = bool(workload.kwargs)
    duplicate_keyword_field = _expected_duplicate_pattern_helper_keyword_field(workload)

    def compile_pattern() -> Any:
        return module.compile(pattern, workload.flags)

    def invoke(compiled: Any) -> object:
        resolved_haystack = (
            static_haystack
            if static_haystack is not None
            else workload.haystack_payload()
        )
        if (
            uses_positional_window
            and workload.operation not in _PATTERN_HELPER_WINDOW_OPERATIONS
        ):
            raise ValueError(
                "benchmark window arguments are only supported for "
                "pattern.search, pattern.match, pattern.fullmatch, "
                "pattern.findall, and pattern.finditer"
            )
        if (
            uses_keyword_arguments
            and workload.operation not in _PATTERN_HELPER_KEYWORD_OPERATIONS
        ):
            raise ValueError(
                "benchmark workload kwargs are only supported for "
                f"{_PATTERN_HELPER_KEYWORD_OPERATIONS_DESCRIPTION}"
            )

        def window_call_args() -> tuple[Any, ...]:
            args: list[Any] = [resolved_haystack]
            if uses_positional_window:
                args.append(workload.pos_argument())
            if workload.endpos is not None:
                args.append(workload.endpos_argument())
            return tuple(args)

        def keyword_call_kwargs() -> dict[str, Any]:
            if not uses_keyword_arguments:
                return {}
            return workload.keyword_arguments()

        if workload.operation == "pattern.search":
            if uses_keyword_arguments:
                return compiled.search(
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            return compiled.search(*window_call_args())
        if workload.operation == "pattern.match":
            if uses_keyword_arguments:
                return compiled.match(
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            if uses_positional_window:
                return compiled.match(*window_call_args())
            return compiled.match(resolved_haystack)
        if workload.operation == "pattern.fullmatch":
            if uses_keyword_arguments:
                return compiled.fullmatch(
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            return compiled.fullmatch(*window_call_args())
        if workload.operation == "pattern.split":
            if uses_keyword_arguments:
                if duplicate_keyword_field == "maxsplit":
                    return compiled.split(
                        resolved_haystack,
                        workload.maxsplit_argument(),
                        **keyword_call_kwargs(),
                    )
                return compiled.split(
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            return compiled.split(
                resolved_haystack,
                workload.maxsplit_argument(),
            )
        if workload.operation == "pattern.findall":
            if uses_keyword_arguments:
                return compiled.findall(
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            return compiled.findall(*window_call_args())
        if workload.operation == "pattern.finditer":
            if uses_keyword_arguments:
                return list(
                    compiled.finditer(
                        resolved_haystack,
                        **keyword_call_kwargs(),
                    )
                )
            return list(compiled.finditer(*window_call_args()))
        if workload.operation == "pattern.sub":
            if uses_keyword_arguments:
                if duplicate_keyword_field == "count":
                    return compiled.sub(
                        workload.replacement_payload(),
                        resolved_haystack,
                        workload.count_argument(),
                        **keyword_call_kwargs(),
                    )
                return compiled.sub(
                    workload.replacement_payload(),
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            return compiled.sub(
                workload.replacement_payload(),
                resolved_haystack,
                workload.count_argument(),
            )
        if workload.operation == "pattern.subn":
            if uses_keyword_arguments:
                if duplicate_keyword_field == "count":
                    return compiled.subn(
                        workload.replacement_payload(),
                        resolved_haystack,
                        workload.count_argument(),
                        **keyword_call_kwargs(),
                    )
                return compiled.subn(
                    workload.replacement_payload(),
                    resolved_haystack,
                    **keyword_call_kwargs(),
                )
            return compiled.subn(
                workload.replacement_payload(),
                resolved_haystack,
                workload.count_argument(),
            )
        raise ValueError(f"unsupported pattern helper operation {workload.operation!r}")

    if workload.cache_mode == "cold":

        def run_once() -> object:
            if hasattr(module, "purge"):
                module.purge()
            compiled = compile_pattern()
            return invoke(compiled)

        return run_once

    if workload.cache_mode == "warm":
        compiled = compile_pattern()

        def run_once() -> object:
            return invoke(compiled)

        return run_once

    if workload.cache_mode == "purged":
        compiled = compile_pattern()
        if hasattr(module, "purge"):
            module.purge()

        def run_once() -> object:
            return invoke(compiled)

        return run_once

    raise ValueError(f"unsupported cache mode {workload.cache_mode!r}")


def build_callable(module: Any, import_name: str, workload: Workload) -> Any:
    if workload.operation == "import":
        return import_callable(import_name, workload)
    if workload.operation in {"compile", "module.compile"}:
        return compile_callable(module, workload)
    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
        "module.split",
        "module.findall",
        "module.finditer",
        "module.sub",
        "module.subn",
    }:
        return helper_callable(module, workload)
    if workload.operation in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.split",
        "pattern.findall",
        "pattern.finditer",
        "pattern.sub",
        "pattern.subn",
    }:
        return pattern_helper_callable(module, workload)
    raise ValueError(f"unsupported benchmark operation {workload.operation!r}")


def _expected_exception_matches(
    exc: Exception,
    expected_exception: dict[str, Any],
) -> bool:
    if type(exc).__name__ != expected_exception["type"]:
        return False

    message_substring = expected_exception.get("message_substring")
    if message_substring is not None and message_substring not in str(exc):
        return False
    return True


def _invoke_timed_callback(workload: Workload, callback: Any) -> None:
    expected_exception = workload.expected_exception
    try:
        callback()
    except Exception as exc:
        if expected_exception is None:
            raise
        if not _expected_exception_matches(exc, expected_exception):
            raise AssertionError(
                f"workload {workload.workload_id!r} raised "
                f"{type(exc).__name__}: {exc!s} instead of the expected "
                f"{expected_exception['type']!r} exception"
            ) from exc
        return

    if expected_exception is not None:
        raise AssertionError(
            f"workload {workload.workload_id!r} did not raise the expected "
            f"{expected_exception['type']!r} exception"
        )


def measure_callable(workload: Workload, callback: Any) -> dict[str, Any]:
    for _ in range(workload.warmup_iterations):
        for _ in range(workload.sample_iterations):
            _invoke_timed_callback(workload, callback)

    sample_ns: list[int] = []
    for _ in range(workload.timed_samples):
        start = time.perf_counter_ns()
        for _ in range(workload.sample_iterations):
            _invoke_timed_callback(workload, callback)
        elapsed_ns = time.perf_counter_ns() - start
        sample_ns.append(max(1, round(elapsed_ns / workload.sample_iterations)))

    median_ns = int(statistics.median(sample_ns))
    mean_ns = int(round(statistics.fmean(sample_ns)))
    return {
        "status": "measured",
        "median_ns": median_ns,
        "mean_ns": mean_ns,
        "min_ns": min(sample_ns),
        "max_ns": max(sample_ns),
        "sample_count": len(sample_ns),
        "warmup_iterations": workload.warmup_iterations,
        "sample_iterations": workload.sample_iterations,
        "samples_ns": sample_ns,
    }


class CpythonReBenchmarkAdapter(BenchmarkAdapter):
    adapter_name = "cpython.re"
    import_name = "re"
    module = cpython_re

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        callback = build_callable(self.module, self.import_name, workload)
        timing = measure_callable(workload, callback)
        return {"adapter": self.adapter_name, **timing}


class RebarBenchmarkAdapter(BenchmarkAdapter):
    adapter_name = "rebar"
    import_name = "rebar"

    def __init__(self, module: Any) -> None:
        self.module = module

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        try:
            callback = build_callable(self.module, self.import_name, workload)
            timing = measure_callable(workload, callback)
        except NotImplementedError as exc:
            return {
                "adapter": self.adapter_name,
                "status": "unimplemented",
                "reason": str(exc),
            }
        except Exception as exc:
            return {
                "adapter": self.adapter_name,
                "status": "unavailable",
                "reason": f"{type(exc).__name__}: {exc}",
            }
        return {"adapter": self.adapter_name, **timing}


class SubprocessBenchmarkAdapter(BenchmarkAdapter):
    """Runs one workload probe in a fresh subprocess environment."""

    def __init__(
        self,
        *,
        adapter_name: str,
        import_name: str,
        python_executable: pathlib.Path,
        pythonpath_entries: list[pathlib.Path],
    ) -> None:
        self.adapter_name = adapter_name
        self.import_name = import_name
        self.python_executable = python_executable
        self.pythonpath_entries = list(pythonpath_entries)

    def _environment(self) -> dict[str, str]:
        env = os.environ.copy()
        pythonpath = os.pathsep.join(str(path) for path in self.pythonpath_entries)
        existing_pythonpath = env.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath = os.pathsep.join((pythonpath, existing_pythonpath))
        env["PYTHONPATH"] = pythonpath
        return env

    def run_workload(self, workload: Workload) -> dict[str, Any]:
        result = subprocess.run(
            [
                str(self.python_executable),
                "-m",
                "rebar_harness.benchmarks",
                "--internal-run-workload",
                json.dumps(workload_to_payload(workload), sort_keys=True),
                "--internal-import-name",
                self.import_name,
                "--internal-adapter-name",
                self.adapter_name,
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=self._environment(),
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown subprocess failure"
            return {
                "adapter": self.adapter_name,
                "status": "unavailable",
                "reason": f"subprocess benchmark probe failed: {detail}",
            }
        return json.loads(result.stdout)


def calculate_speedup(
    baseline_timing: dict[str, Any], implementation_timing: dict[str, Any]
) -> float | None:
    baseline_ns = baseline_timing.get("median_ns")
    implementation_ns = implementation_timing.get("median_ns")
    if not isinstance(baseline_ns, int) or not isinstance(implementation_ns, int):
        return None
    if baseline_ns <= 0 or implementation_ns <= 0:
        return None
    return round(baseline_ns / implementation_ns, 4)


def build_variance_summary(timing: dict[str, Any]) -> dict[str, Any] | None:
    samples = timing.get("samples_ns")
    if not isinstance(samples, list) or not samples:
        return None
    return {
        "min_ns": timing["min_ns"],
        "max_ns": timing["max_ns"],
        "mean_ns": timing["mean_ns"],
        "sample_count": timing["sample_count"],
    }


def ns_to_ops_per_second(value: int | None) -> float | None:
    if not isinstance(value, int) or value <= 0:
        return None
    return round(1_000_000_000 / value, 2)


def gap_note_for_workload(workload: Workload) -> str:
    if workload.family == "parser":
        return (
            "Implementation timing is unavailable for parser cases outside the current "
            "rebar compile surface."
        )
    if workload.operation == "import":
        return "Implementation import timing is unavailable until the rebar package can be imported in the benchmark environment."
    if workload.operation.startswith("pattern."):
        return "Implementation timing is unavailable until the rebar compiled-pattern helper surface performs real work."
    return "Implementation timing is unavailable until the rebar module helper surface performs real work."


def evaluate_workload(
    workload: Workload,
    baseline_adapter: BenchmarkAdapter,
    implementation_adapter: BenchmarkAdapter,
) -> dict[str, Any]:
    baseline_timing = baseline_adapter.run_workload(workload)
    implementation_timing = implementation_adapter.run_workload(workload)
    speedup = calculate_speedup(baseline_timing, implementation_timing)

    status = "measured" if speedup is not None else implementation_timing["status"]
    notes = list(workload.notes)
    if implementation_timing["status"] != "measured":
        notes.append(gap_note_for_workload(workload))

    baseline_ns = baseline_timing.get("median_ns")
    implementation_ns = implementation_timing.get("median_ns")
    result = {
        "id": workload.workload_id,
        "manifest_id": workload.manifest_id,
        "bucket": workload.bucket,
        "family": workload.family,
        "operation": workload.operation,
        "cache_mode": workload.cache_mode,
        "timing_scope": workload.timing_scope,
        "text_model": workload.text_model,
        "pattern": workload.pattern,
        "haystack": workload.haystack,
        "replacement": workload.replacement,
        "expected_exception": workload.expected_exception,
        "flags": workload.flags,
        "count": workload.count,
        "maxsplit": workload.maxsplit,
        "categories": workload.categories,
        "syntax_features": workload.syntax_features,
        "status": status,
        "baseline_ns": baseline_ns,
        "baseline_ops_per_second": ns_to_ops_per_second(baseline_ns),
        "implementation_ns": implementation_ns,
        "implementation_ops_per_second": ns_to_ops_per_second(implementation_ns),
        "speedup_vs_cpython": speedup,
        "notes": notes,
        "baseline_timing": baseline_timing,
        "implementation_timing": implementation_timing,
        "variance": {
            "baseline": build_variance_summary(baseline_timing),
            "implementation": build_variance_summary(implementation_timing),
        },
    }
    if workload.pos is not None:
        result["pos"] = workload.pos
    if workload.endpos is not None:
        result["endpos"] = workload.endpos
    if workload.kwargs:
        result["kwargs"] = dict(workload.kwargs)
    if workload.haystack_text_model is not None:
        result["haystack_text_model"] = workload.haystack_text_model
    return result


def _median(values: list[int]) -> int | None:
    if not values:
        return None
    return int(statistics.median(values))


def _median_float(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(statistics.median(values)), 4)


def _geomean(values: list[float]) -> float | None:
    if not values:
        return None
    if any(value <= 0 for value in values):
        return None
    return round(math.exp(statistics.fmean(math.log(value) for value in values)), 4)


def build_cache_mode_summary(workloads: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for cache_mode in ("cold", "warm", "purged"):
        cache_workloads = [workload for workload in workloads if workload["cache_mode"] == cache_mode]
        baseline_samples = [
            workload["baseline_ns"]
            for workload in cache_workloads
            if isinstance(workload.get("baseline_ns"), int)
        ]
        implementation_samples = [
            workload["implementation_ns"]
            for workload in cache_workloads
            if isinstance(workload.get("implementation_ns"), int)
        ]
        speedups = [
            workload["speedup_vs_cpython"]
            for workload in cache_workloads
            if isinstance(workload.get("speedup_vs_cpython"), float)
        ]
        summary[cache_mode] = {
            "workload_count": len(cache_workloads),
            "known_gap_count": sum(1 for workload in cache_workloads if workload["status"] != "measured"),
            "median_baseline_ns": _median(baseline_samples),
            "median_implementation_ns": _median(implementation_samples),
            "median_speedup_vs_cpython": _median_float(speedups),
        }
    return summary


def family_readiness(family_workloads: list[dict[str, Any]], known_gap_count: int) -> str:
    if not family_workloads:
        return "absent"
    if known_gap_count == 0:
        return "measured"
    if known_gap_count < len(family_workloads):
        return "partial"
    return "scaffold-only"


def family_notes(family: str, family_workloads: list[dict[str, Any]]) -> list[str]:
    if family == "parser":
        return [
            "Phase 1 compile-path suite uses compile() as a parser proxy until a narrower benchmark hook exists."
        ]
    if family_workloads:
        return [
            "Phase 2 module-boundary timings use tiny import and helper-call workloads so the scorecard stays focused on public API overhead."
        ]
    return ["Module-boundary timings remain deferred to RBR-0015."]


def manifest_notes(manifest: BenchmarkManifest, selected_workloads: list[dict[str, Any]]) -> list[str]:
    configured_notes = list(manifest.notes)
    if configured_notes:
        return configured_notes

    manifest_id = manifest.manifest_id
    if manifest_id == "compile-matrix":
        return [
            "Compile-path workloads remain the parser proxy portion of the suite until a narrower parser hook exists."
        ]
    if manifest_id == "module-boundary":
        return [
            "Module-boundary workloads keep haystacks intentionally small so the timings emphasize public helper overhead."
        ]
    if manifest_id == "pattern-boundary":
        return [
            "Pattern-boundary workloads precompile tiny literal patterns ahead of the timed call so the scorecard isolates bound-method overhead from module helper and compile costs."
        ]
    if selected_workloads:
        return [
            "Regression/stability workloads track small, curated performance-cliff probes instead of broad engine-throughput claims."
        ]
    return []


def build_family_summary(workloads: list[dict[str, Any]], family: str) -> dict[str, Any]:
    family_workloads = [workload for workload in workloads if workload["family"] == family]
    baseline_samples = [
        workload["baseline_ns"]
        for workload in family_workloads
        if isinstance(workload.get("baseline_ns"), int)
    ]
    implementation_samples = [
        workload["implementation_ns"]
        for workload in family_workloads
        if isinstance(workload.get("implementation_ns"), int)
    ]
    speedups = [
        workload["speedup_vs_cpython"]
        for workload in family_workloads
        if isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    known_gap_count = sum(1 for workload in family_workloads if workload["status"] != "measured")

    return {
        "workload_count": len(family_workloads),
        "known_gap_count": known_gap_count,
        "readiness": family_readiness(family_workloads, known_gap_count),
        "median_baseline_ns": _median(baseline_samples),
        "median_implementation_ns": _median(implementation_samples),
        "median_speedup_vs_cpython": _median_float(speedups),
        "cache_modes": build_cache_mode_summary(family_workloads),
        "notes": family_notes(family, family_workloads),
    }

def build_manifest_summaries(
    *,
    manifests: list[BenchmarkManifest],
    workloads: list[dict[str, Any]],
    selection_mode: str,
) -> dict[str, dict[str, Any]]:
    manifest_map = {manifest.manifest_id: manifest for manifest in manifests}
    summaries: dict[str, dict[str, Any]] = {}

    for manifest_id, manifest in manifest_map.items():
        manifest_workloads = [
            workload for workload in workloads if workload["manifest_id"] == manifest_id
        ]
        speedups = [
            workload["speedup_vs_cpython"]
            for workload in manifest_workloads
            if isinstance(workload.get("speedup_vs_cpython"), float)
        ]
        known_gap_count = sum(1 for workload in manifest_workloads if workload["status"] != "measured")
        smoke_workload_ids = manifest.smoke_workload_ids()

        summaries[manifest_id] = {
            "workload_count": len(manifest.workloads),
            "selected_workload_count": len(manifest_workloads),
            "measured_workloads": len(speedups),
            "known_gap_count": known_gap_count,
            "readiness": family_readiness(manifest_workloads, known_gap_count),
            "median_speedup_vs_cpython": _median_float(speedups),
            "families": sorted({str(workload["family"]) for workload in manifest_workloads}),
            "operations": sorted({str(workload["operation"]) for workload in manifest_workloads}),
            "selection_mode": selection_mode,
            "smoke_workload_ids": smoke_workload_ids,
            "available_smoke_workload_count": len(smoke_workload_ids),
            "spec_refs": list(manifest.spec_refs),
            "notes": manifest_notes(manifest, manifest_workloads),
        }

    return summaries


def build_summary(workloads: list[dict[str, Any]]) -> dict[str, Any]:
    parser_speedups = [
        workload["speedup_vs_cpython"]
        for workload in workloads
        if workload["family"] == "parser" and isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    module_speedups = [
        workload["speedup_vs_cpython"]
        for workload in workloads
        if workload["family"] == "module" and isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    all_speedups = [
        workload["speedup_vs_cpython"]
        for workload in workloads
        if isinstance(workload.get("speedup_vs_cpython"), float)
    ]
    baseline_samples = [
        workload["baseline_ns"] for workload in workloads if isinstance(workload.get("baseline_ns"), int)
    ]
    implementation_samples = [
        workload["implementation_ns"]
        for workload in workloads
        if isinstance(workload.get("implementation_ns"), int)
    ]
    known_gap_count = sum(1 for workload in workloads if workload["status"] != "measured")
    baseline_median_ns = _median(baseline_samples)
    implementation_median_ns = _median(implementation_samples)
    return {
        "total_workloads": len(workloads),
        "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
        "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
        "regression_workloads": sum(
            1 for workload in workloads if workload["manifest_id"] == "regression-matrix"
        ),
        "measured_workloads": len(all_speedups),
        "known_gap_count": known_gap_count,
        "baseline_median_ns": baseline_median_ns,
        "baseline_median_ops_per_second": ns_to_ops_per_second(baseline_median_ns),
        "implementation_median_ns": implementation_median_ns,
        "implementation_median_ops_per_second": ns_to_ops_per_second(implementation_median_ns),
        "median_speedup_vs_baseline": _median_float(all_speedups),
        "geomean_speedup_vs_baseline": _geomean(all_speedups),
        "parser_median_speedup_vs_cpython": _median_float(parser_speedups),
        "module_median_speedup_vs_cpython": _median_float(module_speedups),
        "workloads_by_cache_mode": {
            cache_mode: sum(1 for workload in workloads if workload["cache_mode"] == cache_mode)
            for cache_mode in ("cold", "warm", "purged")
        },
    }


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def cpu_model() -> str:
    cpuinfo_path = pathlib.Path("/proc/cpuinfo")
    if cpuinfo_path.is_file():
        for line in cpuinfo_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                _, _, value = line.partition(":")
                return value.strip()
    return platform.processor() or "unknown"


def determine_phase(workloads: list[dict[str, Any]]) -> str:
    if any(workload["manifest_id"] == "regression-matrix" for workload in workloads):
        return "phase3-regression-stability-suite"
    if any(workload["family"] == "module" for workload in workloads):
        return "phase2-module-boundary-suite"
    return "phase1-compile-path-suite"


def determine_runner_version(workloads: list[dict[str, Any]]) -> str:
    if any(workload["manifest_id"] == "regression-matrix" for workload in workloads):
        return "phase3"
    if any(workload["family"] == "module" for workload in workloads):
        return "phase2"
    return "phase1"


def probe_loaded_rebar_metadata(module: Any) -> dict[str, Any]:
    native_loaded = bool(module.native_module_loaded())
    native_module_name = getattr(module, "NATIVE_MODULE_NAME", NATIVE_MODULE_NAME)
    native_scaffold_status = module.native_scaffold_status()
    native_target_cpython_series = module.native_target_cpython_series()
    return {
        "native_module_loaded": native_loaded,
        "native_module_name": native_module_name,
        "native_scaffold_status": native_scaffold_status,
        "native_target_cpython_series": native_target_cpython_series,
    }


def workload_family(workload: dict[str, Any] | Workload) -> str:
    if isinstance(workload, Workload):
        return workload.family
    return str(workload["family"])


def source_tree_metadata(
    *,
    workloads: list[dict[str, Any]] | list[Workload],
    requested_mode: str,
    native_unavailable_reason: str | None,
) -> dict[str, Any]:
    module = importlib.import_module("rebar")
    probed = probe_loaded_rebar_metadata(module)
    includes_module_boundary = any(workload_family(workload) == "module" for workload in workloads)
    return {
        "module_name": "rebar",
        "adapter": "rebar.module-surface" if includes_module_boundary else "rebar.compile",
        "adapter_mode_requested": requested_mode,
        "adapter_mode_resolved": SOURCE_TREE_SHIM_MODE,
        "build_mode": SOURCE_TREE_SHIM_MODE,
        "timing_path": SOURCE_TREE_SHIM_MODE,
        "native_unavailable_reason": native_unavailable_reason,
        "native_build_tool": None,
        "native_wheel": None,
        "git_commit": git_commit(),
        **probed,
    }


def _clean_failure_message(label: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = result.stderr.strip() or result.stdout.strip() or f"{label} failed"
    return f"{label} failed: {detail}"


def _pythonpath_env(entries: list[pathlib.Path]) -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = os.pathsep.join(str(entry) for entry in entries)
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath = os.pathsep.join((pythonpath, existing_pythonpath))
    env["PYTHONPATH"] = pythonpath
    return env


def _native_runtime_failure(
    temp_dir: tempfile.TemporaryDirectory,
    reason: str,
) -> tuple[None, None, str]:
    temp_dir.cleanup()
    return None, None, reason


def provision_built_native_runtime() -> tuple[dict[str, Any] | None, tempfile.TemporaryDirectory | None, str | None]:
    maturin = shutil.which("maturin")
    if maturin is None:
        return None, None, "built-native mode unavailable because no `maturin` executable was found on PATH"

    temp_dir = tempfile.TemporaryDirectory(prefix="rebar-bench-native-")
    temp_root = pathlib.Path(temp_dir.name)
    wheelhouse = temp_root / "wheelhouse"
    install_root = temp_root / "site-packages"
    wheelhouse.mkdir(parents=True, exist_ok=True)
    install_root.mkdir(parents=True, exist_ok=True)

    build_result = subprocess.run(
        [
            maturin,
            "build",
            "--manifest-path",
            "crates/rebar-cpython/Cargo.toml",
            "--interpreter",
            sys.executable,
            "--out",
            str(wheelhouse),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if build_result.returncode != 0:
        return _native_runtime_failure(
            temp_dir,
            _clean_failure_message("maturin build", build_result),
        )

    wheels = sorted(wheelhouse.glob("rebar-*.whl"))
    if len(wheels) != 1:
        return _native_runtime_failure(
            temp_dir,
            f"built-native mode unavailable because wheel build produced {len(wheels)} rebar wheels",
        )

    install_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(install_root),
            str(wheels[0]),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if install_result.returncode != 0:
        return _native_runtime_failure(
            temp_dir,
            _clean_failure_message("pip install --target", install_result),
        )

    probe_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rebar_harness.benchmarks",
            "--internal-probe-rebar-metadata",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=_pythonpath_env([install_root, PYTHON_SOURCE]),
    )
    if probe_result.returncode != 0:
        return _native_runtime_failure(
            temp_dir,
            _clean_failure_message("native metadata probe", probe_result),
        )

    probed = json.loads(probe_result.stdout)
    if not probed.get("native_module_loaded", False):
        return _native_runtime_failure(
            temp_dir,
            "built-native mode unavailable because the installed wheel did not load `rebar._rebar`",
        )

    return {
        "install_root": install_root,
        "maturin_path": pathlib.Path(maturin),
        "wheel_name": wheels[0].name,
        "probe": probed,
    }, temp_dir, None


def prepare_benchmark_run(
    *,
    workloads: list[Workload],
    adapter_mode: str,
    allow_fallback: bool = True,
) -> BenchmarkRunContext:
    requested_mode = adapter_mode
    if adapter_mode == BUILT_NATIVE_MODE:
        provisioned, temp_dir, native_error = provision_built_native_runtime()
        if provisioned is not None and temp_dir is not None:
            includes_module_boundary = any(workload.family == "module" for workload in workloads)
            probe = provisioned["probe"]
            return BenchmarkRunContext(
                requested_mode=BUILT_NATIVE_MODE,
                resolved_mode=BUILT_NATIVE_MODE,
                baseline_adapter=SubprocessBenchmarkAdapter(
                    adapter_name="cpython.re",
                    import_name="re",
                    python_executable=pathlib.Path(sys.executable),
                    pythonpath_entries=[PYTHON_SOURCE],
                ),
                implementation_adapter=SubprocessBenchmarkAdapter(
                    adapter_name="rebar",
                    import_name="rebar",
                    python_executable=pathlib.Path(sys.executable),
                    pythonpath_entries=[provisioned["install_root"], PYTHON_SOURCE],
                ),
                implementation_metadata={
                    "module_name": "rebar",
                    "adapter": "rebar.module-surface" if includes_module_boundary else "rebar.compile",
                    "adapter_mode_requested": BUILT_NATIVE_MODE,
                    "adapter_mode_resolved": BUILT_NATIVE_MODE,
                    "build_mode": BUILT_NATIVE_MODE,
                    "timing_path": BUILT_NATIVE_MODE,
                    "native_unavailable_reason": None,
                    "native_build_tool": "maturin",
                    "native_wheel": provisioned["wheel_name"],
                    "git_commit": git_commit(),
                    **probe,
                },
                execution_model="single-interpreter subprocess workload probes against a built native wheel",
                cleanup=temp_dir.cleanup,
            )
        if not allow_fallback:
            raise NativeBenchmarkProvisionError(
                native_error or "built-native mode unavailable for the requested benchmark run"
            )
        native_unavailable_reason = native_error
    else:
        native_unavailable_reason = (
            "built-native timing path not requested; using the default source-tree shim"
        )

    return BenchmarkRunContext(
        requested_mode=requested_mode,
        resolved_mode=SOURCE_TREE_SHIM_MODE,
        baseline_adapter=CpythonReBenchmarkAdapter(),
        implementation_adapter=RebarBenchmarkAdapter(importlib.import_module("rebar")),
        implementation_metadata=source_tree_metadata(
            workloads=workloads,
            requested_mode=requested_mode,
            native_unavailable_reason=native_unavailable_reason,
        ),
        execution_model="single-process in-process adapter comparison",
        cleanup=lambda: None,
    )


def run_internal_workload_probe(
    *,
    workload_payload: str,
    import_name: str,
    adapter_name: str,
) -> dict[str, Any]:
    workload = workload_from_payload(json.loads(workload_payload))
    try:
        module = cpython_re if import_name == "re" else importlib.import_module(import_name)
        callback = build_callable(module, import_name, workload)
        timing = measure_callable(workload, callback)
    except NotImplementedError as exc:
        return {
            "adapter": adapter_name,
            "status": "unimplemented",
            "reason": str(exc),
        }
    except Exception as exc:
        return {
            "adapter": adapter_name,
            "status": "unavailable",
            "reason": f"{type(exc).__name__}: {exc}",
        }
    return {"adapter": adapter_name, **timing}


def run_internal_rebar_metadata_probe() -> dict[str, Any]:
    module = importlib.import_module("rebar")
    return {
        "module_name": "rebar",
        **probe_loaded_rebar_metadata(module),
    }


def build_scorecard(
    *,
    manifests: list[BenchmarkManifest],
    workloads: list[dict[str, Any]],
    selection_mode: str,
    implementation_metadata: dict[str, Any],
    execution_model: str,
) -> dict[str, Any]:
    summary = build_summary(workloads)
    deferred: list[dict[str, str]] = []
    if not any(workload["family"] == "module" for workload in workloads):
        deferred.append(
            {
                "area": "module-boundary",
                "reason": "Phase 1 benchmark suite measures compile-path workloads only.",
                "follow_up": "RBR-0015",
            }
        )
    deferred.append(
        {
            "area": "regex-execution-throughput",
            "reason": "Execution benchmarks stay deferred until parser and module-boundary harnesses exist.",
            "follow_up": "future milestone",
        }
    )
    manifest_records = [
        {
            "manifest": str(manifest.path.relative_to(REPO_ROOT)),
            "manifest_id": manifest.manifest_id,
            "manifest_schema_version": manifest.schema_version,
            "workload_count": len(manifest.workloads),
            "smoke_workload_ids": manifest.smoke_workload_ids(),
            "spec_refs": list(manifest.spec_refs),
        }
        for manifest in manifests
    ]
    artifacts: dict[str, Any]
    if len(manifest_records) == 1:
        artifacts = {
            **manifest_records[0],
            "manifests": manifest_records,
            "raw_samples": None,
            "selection_mode": selection_mode,
        }
    else:
        artifacts = {
            "manifest": None,
            "manifest_id": "combined-benchmark-suite",
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "manifests": manifest_records,
            "raw_samples": None,
            "selection_mode": selection_mode,
        }
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "suite": "benchmarks",
        "phase": determine_phase(workloads),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.benchmarks",
        "baseline": build_cpython_baseline(version_family=TARGET_CPYTHON_SERIES),
        "implementation": implementation_metadata,
        "environment": {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "cpu_model": cpu_model(),
            "logical_cpus": os.cpu_count(),
            "runner": "perf_counter_ns",
            "runner_version": determine_runner_version(workloads),
            "execution_model": execution_model,
        },
        "summary": summary,
        "manifests": build_manifest_summaries(
            manifests=manifests,
            workloads=workloads,
            selection_mode=selection_mode,
        ),
        "families": {
            "parser": build_family_summary(workloads, "parser"),
            "module": build_family_summary(workloads, "module"),
        },
        "cache_modes": build_cache_mode_summary(workloads),
        "workloads": workloads,
        "deferred": deferred,
        "artifacts": artifacts,
    }


def run_benchmarks(
    manifest_paths: list[pathlib.Path] | None = None,
    report_path: pathlib.Path | None = DEFAULT_REPORT_PATH,
    *,
    smoke_only: bool = False,
    adapter_mode: str = SOURCE_TREE_SHIM_MODE,
    allow_fallback: bool = True,
) -> dict[str, Any]:
    default_manifest_paths = list(
        select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)
    )
    resolved_manifest_paths = [
        path.resolve() for path in (manifest_paths or default_manifest_paths)
    ]
    resolved_report_path = SCORECARD_REPORT.resolve_optional_path(report_path)
    manifests = load_manifests(resolved_manifest_paths)
    selected_manifest_workloads = select_workloads(
        [workload for manifest in manifests for workload in manifest.workloads],
        smoke_only=smoke_only,
    )
    run_context = prepare_benchmark_run(
        workloads=selected_manifest_workloads,
        adapter_mode=adapter_mode,
        allow_fallback=allow_fallback,
    )
    try:
        workloads = [
            evaluate_workload(
                workload,
                run_context.baseline_adapter,
                run_context.implementation_adapter,
            )
            for workload in selected_manifest_workloads
        ]
        scorecard = build_scorecard(
            manifests=manifests,
            workloads=workloads,
            selection_mode="smoke" if smoke_only else "full",
            implementation_metadata=run_context.implementation_metadata,
            execution_model=run_context.execution_model,
        )
        if resolved_report_path is not None:
            SCORECARD_REPORT.write(scorecard, resolved_report_path)
        return scorecard
    finally:
        run_context.cleanup()


def run_built_native_smoke_benchmarks(
    report_path: pathlib.Path | None = None,
) -> dict[str, Any]:
    return run_benchmarks(
        manifest_paths=list(
            select_benchmark_manifest_paths(BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR)
        ),
        report_path=report_path,
        smoke_only=True,
        adapter_mode=BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def run_built_native_full_benchmarks(
    report_path: pathlib.Path | None = None,
) -> dict[str, Any]:
    return run_benchmarks(
        manifest_paths=list(
            select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)
        ),
        report_path=report_path,
        smoke_only=False,
        adapter_mode=BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        action="append",
        default=None,
        help="Path to a benchmark workload manifest. Repeat to combine multiple manifests.",
    )
    parser.add_argument(
        "--report",
        type=pathlib.Path,
        default=None,
        help=(
            "Path to the output scorecard. Ordinary runs default to "
            "`reports/benchmarks/latest.py`; explicit `.py` and temporary `.json` outputs "
            "remain supported, and strict built-native modes only write a report when you pass "
            "this flag explicitly."
        ),
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run only workloads tagged as smoke within the selected manifests.",
    )
    parser.add_argument(
        "--adapter-mode",
        choices=(SOURCE_TREE_SHIM_MODE, BUILT_NATIVE_MODE),
        default=SOURCE_TREE_SHIM_MODE,
        help=(
            "Benchmark the source-tree shim or provision a built native wheel when possible. "
            "The default keeps the existing source-tree shim path."
        ),
    )
    parser.add_argument(
        "--native-smoke",
        action="store_true",
        help=(
            "Run the dedicated built-native smoke slice against the tracked smoke manifests. "
            "This mode requires a real built native wheel and returns an in-memory scorecard "
            "unless you pass --report."
        ),
    )
    parser.add_argument(
        "--native-full",
        action="store_true",
        help=(
            "Run the full combined benchmark suite against a real built native wheel. "
            "This mode requires a real built native wheel and returns an in-memory scorecard "
            "unless you pass --report."
        ),
    )
    parser.add_argument(
        "--internal-run-workload",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--internal-import-name",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--internal-adapter-name",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--internal-probe-rebar-metadata",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.internal_probe_rebar_metadata:
        print(json.dumps(run_internal_rebar_metadata_probe(), sort_keys=True))
        return 0
    if args.internal_run_workload is not None:
        if args.internal_import_name is None or args.internal_adapter_name is None:
            raise SystemExit(
                "--internal-run-workload requires --internal-import-name and --internal-adapter-name"
            )
        print(
            json.dumps(
                run_internal_workload_probe(
                    workload_payload=args.internal_run_workload,
                    import_name=args.internal_import_name,
                    adapter_name=args.internal_adapter_name,
                ),
                sort_keys=True,
            )
        )
        return 0
    if args.native_smoke and args.native_full:
        raise SystemExit("--native-smoke and --native-full are mutually exclusive")
    try:
        if args.native_smoke:
            if args.manifest is not None:
                raise SystemExit("--native-smoke cannot be combined with --manifest")
            if args.smoke:
                raise SystemExit("--native-smoke already implies smoke-only selection")
            if args.adapter_mode != SOURCE_TREE_SHIM_MODE:
                raise SystemExit("--native-smoke manages adapter selection itself")
            scorecard = run_built_native_smoke_benchmarks(report_path=args.report)
        elif args.native_full:
            if args.manifest is not None:
                raise SystemExit("--native-full cannot be combined with --manifest")
            if args.smoke:
                raise SystemExit("--native-full runs the full suite and cannot be combined with --smoke")
            if args.adapter_mode != SOURCE_TREE_SHIM_MODE:
                raise SystemExit("--native-full manages adapter selection itself")
            scorecard = run_built_native_full_benchmarks(report_path=args.report)
        else:
            scorecard = run_benchmarks(
                manifest_paths=args.manifest,
                report_path=args.report or DEFAULT_REPORT_PATH,
                smoke_only=args.smoke,
                adapter_mode=args.adapter_mode,
            )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    smoke_summary = {
        "total_workloads": scorecard["summary"]["total_workloads"],
        "parser_workloads": scorecard["summary"]["parser_workloads"],
        "module_workloads": scorecard["summary"]["module_workloads"],
        "regression_workloads": scorecard["summary"]["regression_workloads"],
        "measured_workloads": scorecard["summary"]["measured_workloads"],
        "known_gap_count": scorecard["summary"]["known_gap_count"],
    }
    print(json.dumps(smoke_summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
