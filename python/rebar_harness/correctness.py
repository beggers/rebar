"""Differential correctness harness for parser and Python-visible `re` behavior."""

from __future__ import annotations

import argparse
import json
import pathlib
import re as cpython_re
import sys
import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Iterable, Sequence


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

import rebar
from rebar_harness.metadata import build_cpython_baseline
from rebar_harness.systematic_corpus import expand_systematic_manifest


TARGET_CPYTHON_SERIES = "3.12.x"
REPORT_SCHEMA_VERSION = "1.0"
FIXTURE_SCHEMA_VERSION = 1
DEFAULT_FIXTURE_PATHS = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "public_api_surface.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "match_behavior_smoke.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "exported_symbol_surface.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "pattern_object_surface.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "module_workflow_surface.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "collection_replacement_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "literal_flag_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_match_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "named_group_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "named_group_replacement_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "named_backreference_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "numbered_backreference_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_segment_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "nested_group_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_callable_replacement_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "literal_alternation_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_alternation_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_alternation_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "grouped_alternation_callable_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "branch_local_backreference_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_branch_local_backreference_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_branch_local_backreference_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "optional_group_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "exact_repeat_quantified_group_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "exact_repeat_quantified_group_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "ranged_repeat_quantified_group_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "wider_ranged_repeat_quantified_group_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "optional_group_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "optional_group_alternation_branch_local_backreference_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_no_else_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_no_else_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_no_else_nested_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_alternation_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_nested_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_quantified_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_no_else_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_no_else_quantified_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_nested_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_quantified_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_yes_else_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_yes_else_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_yes_else_nested_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_yes_else_quantified_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_fully_empty_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_fully_empty_quantified_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_fully_empty_nested_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_nested_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_yes_else_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_fully_empty_replacement_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_fully_empty_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_assertion_diagnostics.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_quantified_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_quantified_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_conditional_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_branch_local_backreference_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_nested_branch_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_backtracking_heavy_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_broader_range_workflows.json",
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_open_ended_workflows.json",
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "systematic_feature_corpus.json",
)
DEFAULT_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"
PHASE_BY_LAYER = {
    "parser_acceptance_and_diagnostics": "phase1-parser-conformance-pack",
    "module_api_surface": "phase2-public-api-surface-pack",
    "pattern_object_parity": "phase2-pattern-object-pack",
    "match_behavior": "phase3-match-behavior-pack",
    "module_workflow": "phase3-module-workflow-pack",
    "regression_and_coverage": "phase4-regression-and-coverage-pack",
}
PHASE_ORDER = tuple(PHASE_BY_LAYER)


@dataclass(frozen=True)
class FixtureManifest:
    path: pathlib.Path
    manifest_id: str
    layer: str
    suite_id: str
    schema_version: int
    defaults: dict[str, Any]
    raw: dict[str, Any]


@dataclass(frozen=True)
class FixtureCase:
    """Single differential correctness case."""

    case_id: str
    manifest_id: str
    suite_id: str
    layer: str
    family: str
    operation: str
    notes: list[str]
    categories: list[str]
    pattern: str | None
    flags: int | None
    text_model: str | None
    pattern_encoding: str
    helper: str | None
    args: list[Any]
    kwargs: dict[str, Any]

    @classmethod
    def from_dict(cls, manifest: FixtureManifest, raw_case: dict[str, Any]) -> "FixtureCase":
        defaults = manifest.defaults
        return cls(
            case_id=str(raw_case["id"]),
            manifest_id=manifest.manifest_id,
            suite_id=str(raw_case.get("suite_id", manifest.suite_id)),
            layer=str(raw_case.get("layer", manifest.layer)),
            family=str(raw_case.get("family", defaults.get("family", manifest.manifest_id))),
            operation=str(raw_case.get("operation", defaults.get("operation", "compile"))),
            notes=[str(note) for note in raw_case.get("notes", [])],
            categories=[str(category) for category in raw_case.get("categories", [])],
            pattern=_optional_string(raw_case.get("pattern")),
            flags=_optional_int(raw_case.get("flags", defaults.get("flags"))),
            text_model=_optional_string(raw_case.get("text_model", defaults.get("text_model"))),
            pattern_encoding=str(
                raw_case.get(
                    "pattern_encoding",
                    defaults.get("pattern_encoding", "latin-1"),
                )
            ),
            helper=_optional_string(raw_case.get("helper")),
            args=_materialize_fixture_value(raw_case.get("args", defaults.get("args", []))),
            kwargs=_materialize_fixture_value(raw_case.get("kwargs", defaults.get("kwargs", {}))),
        )

    def pattern_payload(self) -> str | bytes:
        if self.pattern is None:
            raise ValueError(f"case {self.case_id!r} is missing a pattern payload")
        if self.text_model == "str":
            return self.pattern
        if self.text_model == "bytes":
            return self.pattern.encode(self.pattern_encoding)
        raise ValueError(f"unsupported text model {self.text_model!r}")

    def serialized_args(self) -> list[Any]:
        return [_normalize_value(argument) for argument in self.args]

    def serialized_kwargs(self) -> dict[str, Any]:
        return {key: _normalize_value(value) for key, value in sorted(self.kwargs.items())}


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _materialize_fixture_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_materialize_fixture_value(item) for item in value]
    if isinstance(value, dict):
        value_type = value.get("type")
        if value_type == "bytes":
            encoding = str(value.get("encoding", "latin-1"))
            return str(value["value"]).encode(encoding)
        if value_type == "callable_constant":
            constant_value = _materialize_fixture_value(value.get("value"))

            def _callable_constant(_match: Any, *, _value: Any = constant_value) -> Any:
                return _value

            _callable_constant.__name__ = "callable_constant"
            _callable_constant.__qualname__ = "callable_constant"
            return _callable_constant
        if value_type == "callable_match_group":
            group_reference = value.get("group", 0)
            prefix = _materialize_fixture_value(value.get("prefix", ""))
            suffix = _materialize_fixture_value(value.get("suffix", ""))

            def _callable_match_group(
                match: Any,
                *,
                _group_reference: Any = group_reference,
                _prefix: Any = prefix,
                _suffix: Any = suffix,
            ) -> Any:
                return _prefix + match.group(_group_reference) + _suffix

            _callable_match_group.__name__ = "callable_match_group"
            _callable_match_group.__qualname__ = "callable_match_group"
            return _callable_match_group
        return {
            str(key): _materialize_fixture_value(item_value)
            for key, item_value in value.items()
        }
    return value


def load_fixture_manifest(path: pathlib.Path) -> tuple[FixtureManifest, list[FixtureCase]]:
    raw_manifest = expand_systematic_manifest(json.loads(path.read_text(encoding="utf-8")))
    schema_version = raw_manifest.get("schema_version")
    if schema_version != FIXTURE_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported fixture schema version {schema_version!r}; "
            f"expected {FIXTURE_SCHEMA_VERSION}"
        )

    defaults = raw_manifest.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("fixture manifest defaults must be an object")

    default_operation = str(defaults.get("operation", "compile"))
    default_suite_id = str(
        raw_manifest.get(
            "suite_id",
            "parser.compile"
            if raw_manifest.get("layer", "parser_acceptance_and_diagnostics")
            == "parser_acceptance_and_diagnostics"
            and default_operation == "compile"
            else raw_manifest["manifest_id"],
        )
    )

    manifest = FixtureManifest(
        path=path,
        manifest_id=str(raw_manifest["manifest_id"]),
        layer=str(raw_manifest.get("layer", "parser_acceptance_and_diagnostics")),
        suite_id=default_suite_id,
        schema_version=schema_version,
        defaults=defaults,
        raw=raw_manifest,
    )
    cases = [FixtureCase.from_dict(manifest, raw_case) for raw_case in raw_manifest.get("cases", [])]
    return manifest, cases


def load_fixture_manifests(paths: Sequence[pathlib.Path]) -> tuple[list[FixtureManifest], list[FixtureCase]]:
    manifests: list[FixtureManifest] = []
    cases: list[FixtureCase] = []
    for path in paths:
        manifest, manifest_cases = load_fixture_manifest(path)
        manifests.append(manifest)
        cases.extend(manifest_cases)
    return manifests, cases


def normalize_warning_records(records: list[warnings.WarningMessage]) -> list[dict[str, str]]:
    return [
        {
            "category": record.category.__name__,
            "message": str(record.message),
        }
        for record in records
    ]


def normalize_pattern_value(pattern: str | bytes) -> str | dict[str, str]:
    if isinstance(pattern, bytes):
        return {
            "encoding": "latin-1",
            "value": pattern.decode("latin-1"),
        }
    return pattern


def normalize_pattern_metadata(compiled_pattern: Any) -> dict[str, Any]:
    groupindex = getattr(compiled_pattern, "groupindex", {})
    return {
        "pattern": normalize_pattern_value(compiled_pattern.pattern),
        "flags": compiled_pattern.flags,
        "groups": compiled_pattern.groups,
        "groupindex": dict(sorted(groupindex.items())),
        "pattern_type": type(compiled_pattern.pattern).__name__,
    }


def normalize_pattern_object_metadata(compiled_pattern: Any) -> dict[str, Any]:
    return {
        **normalize_pattern_metadata(compiled_pattern),
        "compiled_type": {
            "module": type(compiled_pattern).__module__,
            "qualname": type(compiled_pattern).__qualname__,
            "repr": repr(type(compiled_pattern)),
        },
    }


def normalize_match_metadata(match: Any) -> dict[str, Any]:
    groupindex = getattr(match.re, "groupindex", {})
    payload = {
        "matched": bool(match),
        "group0": _normalize_value(match.group(0)),
        "groups": [_normalize_value(group) for group in match.groups()],
        "groupdict": {
            key: _normalize_value(value) for key, value in sorted(match.groupdict().items())
        },
        "lastgroup": match.lastgroup,
        "lastindex": match.lastindex,
        "pos": match.pos,
        "endpos": match.endpos,
        "span": list(match.span()),
        "string_type": type(match.string).__name__,
    }
    if groupindex:
        payload["named_groups"] = {
            name: _normalize_value(match.group(name)) for name in sorted(groupindex)
        }
        payload["named_group_spans"] = {
            name: list(match.span(name)) for name in sorted(groupindex)
        }
    if match.re.groups >= 1:
        payload["group1"] = _normalize_value(match.group(1))
        payload["span1"] = list(match.span(1))
        payload["group_spans"] = [
            None if span is None else list(span)
            for span in (match.span(group_index) for group_index in range(1, match.re.groups + 1))
        ]
    return payload


def _normalize_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return normalize_pattern_value(value)
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize_value(item) for key, item in sorted(value.items())}
    if callable(value) and not isinstance(value, type):
        return {
            "type": "callable",
            "module": getattr(value, "__module__", type(value).__module__),
            "qualname": getattr(value, "__qualname__", getattr(value, "__name__", type(value).__qualname__)),
        }
    if hasattr(value, "__iter__") and hasattr(value, "__next__"):
        items = [_normalize_value(item) for item in value]
        return {
            "items": items,
            "exhausted": next(value, None) is None,
        }
    if all(hasattr(value, attribute) for attribute in ("pattern", "flags", "groups", "groupindex")):
        return normalize_pattern_metadata(value)
    if all(hasattr(value, attribute) for attribute in ("span", "group", "groups", "groupdict")):
        return normalize_match_metadata(value)
    return {
        "type": type(value).__name__,
        "repr": repr(value),
    }


def normalize_exception(exc: BaseException) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": type(exc).__name__,
        "message": str(exc),
    }
    for attribute in ("pos", "lineno", "colno"):
        if hasattr(exc, attribute):
            value = getattr(exc, attribute)
            if value is not None:
                payload[attribute] = value
    return payload


def normalize_exported_symbol_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {
            "present": False,
            "type_name": None,
            "value": None,
        }

    payload: dict[str, Any] = {
        "present": True,
        "type_name": type(value).__name__,
        "value": _normalize_value(value),
    }
    if hasattr(value, "name"):
        payload["name"] = getattr(value, "name")
    return payload


def normalize_exported_symbol_metadata(value: Any) -> dict[str, Any]:
    if value is None:
        return {
            "present": False,
            "callable": False,
            "is_type": False,
            "type_name": None,
        }

    payload: dict[str, Any] = {
        "present": True,
        "callable": callable(value),
        "is_type": isinstance(value, type),
        "type_name": type(value).__name__,
    }

    if isinstance(value, type):
        payload.update(
            {
                "module": value.__module__,
                "qualname": value.__qualname__,
                "repr": repr(value),
                "mro": [f"{cls.__module__}.{cls.__qualname__}" for cls in value.__mro__],
            }
        )
        if hasattr(value, "__members__"):
            payload["members"] = {
                name: int(member) for name, member in sorted(value.__members__.items())
            }
    else:
        payload["repr"] = repr(value)

    return payload


class Adapter:
    """Adapter boundary for correctness observations."""

    adapter_name: str
    module: Any

    def observe(self, case: FixtureCase) -> dict[str, Any]:
        if case.operation == "cache_workflow":
            return self.observe_cache_workflow(case)
        if case.operation == "cache_distinct_workflow":
            return self.observe_cache_distinct_workflow(case)
        if case.operation == "compile":
            return self.observe_compile(case)
        if case.operation == "pattern_metadata":
            return self.observe_pattern_metadata(case)
        if case.operation == "pattern_call":
            return self.observe_pattern_call(case)
        if case.operation == "purge_workflow":
            return self.observe_purge_workflow(case)
        if case.operation == "module_has_attr":
            return self.observe_module_has_attr(case)
        if case.operation == "module_call":
            return self.observe_module_call(case)
        if case.operation == "module_attr_value":
            return self.observe_module_attr_value(case)
        if case.operation == "module_attr_metadata":
            return self.observe_module_attr_metadata(case)
        raise ValueError(f"unsupported operation {case.operation!r}")

    def observe_compile(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError

    def observe_pattern_metadata(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError

    def observe_pattern_call(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError

    def observe_cache_workflow(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError

    def observe_cache_distinct_workflow(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError

    def observe_purge_workflow(self, case: FixtureCase) -> dict[str, Any]:
        raise NotImplementedError

    def observe_module_has_attr(self, case: FixtureCase) -> dict[str, Any]:
        if case.helper is None:
            raise ValueError(f"case {case.case_id!r} requires a helper name")
        attribute = getattr(self.module, case.helper, None)
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=[],
            result={
                "present": attribute is not None,
                "callable": callable(attribute) if attribute is not None else None,
            },
        )

    def observe_module_call(self, case: FixtureCase) -> dict[str, Any]:
        if case.helper is None:
            raise ValueError(f"case {case.case_id!r} requires a helper name")

        helper = getattr(self.module, case.helper)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                result = helper(*case.args, **case.kwargs)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=_normalize_value(result),
        )

    def observe_module_attr_value(self, case: FixtureCase) -> dict[str, Any]:
        if case.helper is None:
            raise ValueError(f"case {case.case_id!r} requires a helper name")

        attribute = getattr(self.module, case.helper, None)
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=[],
            result=normalize_exported_symbol_value(attribute),
        )

    def observe_module_attr_metadata(self, case: FixtureCase) -> dict[str, Any]:
        if case.helper is None:
            raise ValueError(f"case {case.case_id!r} requires a helper name")

        attribute = getattr(self.module, case.helper, None)
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=[],
            result=normalize_exported_symbol_metadata(attribute),
        )

    def _purge_module_cache(self) -> Any:
        purge_helper = getattr(self.module, "purge")
        return purge_helper()


class CpythonReAdapter(Adapter):
    adapter_name = "cpython.re"
    module = cpython_re

    def _compile_pattern(self, case: FixtureCase) -> Any:
        return cpython_re.compile(case.pattern_payload(), case.flags or 0)

    def observe_compile(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = self._compile_pattern(case)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=normalize_pattern_metadata(compiled),
        )

    def observe_pattern_metadata(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = self._compile_pattern(case)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=normalize_pattern_object_metadata(compiled),
        )

    def observe_pattern_call(self, case: FixtureCase) -> dict[str, Any]:
        if case.helper is None:
            raise ValueError(f"case {case.case_id!r} requires a helper name")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = self._compile_pattern(case)
                result = getattr(compiled, case.helper)(*case.args, **case.kwargs)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=_normalize_value(result),
        )

    def observe_cache_workflow(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                self._purge_module_cache()
                first = self._compile_pattern(case)
                second = self._compile_pattern(case)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        self._purge_module_cache()
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result={
                "first": normalize_pattern_metadata(first),
                "second": normalize_pattern_metadata(second),
                "same_object": first is second,
            },
        )

    def observe_purge_workflow(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                self._purge_module_cache()
                first = self._compile_pattern(case)
                second = self._compile_pattern(case)
                purge_result = self._purge_module_cache()
                third = self._compile_pattern(case)
                fourth = self._compile_pattern(case)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        self._purge_module_cache()
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result={
                "before_purge": normalize_pattern_metadata(first),
                "before_purge_same_object": first is second,
                "purge_result": _normalize_value(purge_result),
                "after_purge": normalize_pattern_metadata(third),
                "after_purge_new_object": third is not first,
                "after_purge_cache_hit": third is fourth,
            },
        )

    def observe_cache_distinct_workflow(self, case: FixtureCase) -> dict[str, Any]:
        alias_flags = int(case.kwargs.get("alias_flags", case.flags or 0))
        distinct_flags = int(case.kwargs["distinct_flags"])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                self._purge_module_cache()
                first = self._compile_pattern(case)
                alias = cpython_re.compile(case.pattern_payload(), alias_flags)
                distinct = cpython_re.compile(case.pattern_payload(), distinct_flags)
            except Exception as exc:  # pragma: no cover - exercised by fixtures
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        self._purge_module_cache()
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result={
                "first": normalize_pattern_metadata(first),
                "alias": normalize_pattern_metadata(alias),
                "distinct": normalize_pattern_metadata(distinct),
                "same_object_as_alias": first is alias,
                "same_object_as_distinct": first is distinct,
            },
        )


class RebarAdapter(Adapter):
    adapter_name = "rebar"
    module = rebar

    def _compile_pattern(self, case: FixtureCase) -> Any:
        return rebar.compile(case.pattern_payload(), case.flags or 0)

    def observe_compile(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = self._compile_pattern(case)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=normalize_pattern_metadata(compiled),
        )

    def observe_pattern_metadata(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = self._compile_pattern(case)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=normalize_pattern_object_metadata(compiled),
        )

    def observe_pattern_call(self, case: FixtureCase) -> dict[str, Any]:
        if case.helper is None:
            raise ValueError(f"case {case.case_id!r} requires a helper name")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                compiled = self._compile_pattern(case)
                result = getattr(compiled, case.helper)(*case.args, **case.kwargs)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result=_normalize_value(result),
        )

    def observe_cache_workflow(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                self._purge_module_cache()
                first = self._compile_pattern(case)
                second = self._compile_pattern(case)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        self._purge_module_cache()
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result={
                "first": normalize_pattern_metadata(first),
                "second": normalize_pattern_metadata(second),
                "same_object": first is second,
            },
        )

    def observe_purge_workflow(self, case: FixtureCase) -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                self._purge_module_cache()
                first = self._compile_pattern(case)
                second = self._compile_pattern(case)
                purge_result = self._purge_module_cache()
                third = self._compile_pattern(case)
                fourth = self._compile_pattern(case)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        self._purge_module_cache()
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result={
                "before_purge": normalize_pattern_metadata(first),
                "before_purge_same_object": first is second,
                "purge_result": _normalize_value(purge_result),
                "after_purge": normalize_pattern_metadata(third),
                "after_purge_new_object": third is not first,
                "after_purge_cache_hit": third is fourth,
            },
        )

    def observe_cache_distinct_workflow(self, case: FixtureCase) -> dict[str, Any]:
        alias_flags = int(case.kwargs.get("alias_flags", case.flags or 0))
        distinct_flags = int(case.kwargs["distinct_flags"])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                self._purge_module_cache()
                first = self._compile_pattern(case)
                alias = rebar.compile(case.pattern_payload(), alias_flags)
                distinct = rebar.compile(case.pattern_payload(), distinct_flags)
            except NotImplementedError as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="unimplemented",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )
            except Exception as exc:
                return finalize_observation(
                    adapter=self.adapter_name,
                    case=case,
                    outcome="exception",
                    warnings_payload=normalize_warning_records(caught),
                    exception=normalize_exception(exc),
                )

        self._purge_module_cache()
        return finalize_observation(
            adapter=self.adapter_name,
            case=case,
            outcome="success",
            warnings_payload=normalize_warning_records(caught),
            result={
                "first": normalize_pattern_metadata(first),
                "alias": normalize_pattern_metadata(alias),
                "distinct": normalize_pattern_metadata(distinct),
                "same_object_as_alias": first is alias,
                "same_object_as_distinct": first is distinct,
            },
        )


def finalize_observation(
    *,
    adapter: str,
    case: FixtureCase,
    outcome: str,
    warnings_payload: list[dict[str, str]],
    result: dict[str, Any] | list[Any] | str | int | float | bool | None = None,
    exception: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "adapter": adapter,
        "operation": case.operation,
        "outcome": outcome,
        "warnings": warnings_payload,
        "result": result,
        "exception": exception,
    }


def compare_observations(
    cpython_observation: dict[str, Any], rebar_observation: dict[str, Any]
) -> tuple[str, list[str]]:
    if rebar_observation["outcome"] == "unimplemented":
        return "unimplemented", ["rebar adapter reports support as unimplemented"]

    mismatches: list[str] = []
    if cpython_observation["outcome"] != rebar_observation["outcome"]:
        mismatches.append(
            "outcome mismatch: "
            f"{cpython_observation['outcome']} != {rebar_observation['outcome']}"
        )

    if cpython_observation["warnings"] != rebar_observation["warnings"]:
        mismatches.append("warning payload mismatch")

    if cpython_observation["result"] != rebar_observation["result"]:
        mismatches.append("result payload mismatch")

    if cpython_observation["exception"] != rebar_observation["exception"]:
        mismatches.append("exception payload mismatch")

    return ("pass", []) if not mismatches else ("fail", mismatches)


def evaluate_case(case: FixtureCase, cpython_adapter: Adapter, rebar_adapter: Adapter) -> dict[str, Any]:
    cpython_observation = cpython_adapter.observe(case)
    rebar_observation = rebar_adapter.observe(case)
    comparison, mismatch_notes = compare_observations(cpython_observation, rebar_observation)

    result = {
        "id": case.case_id,
        "manifest_id": case.manifest_id,
        "suite_id": case.suite_id,
        "layer": case.layer,
        "family": case.family,
        "operation": case.operation,
        "notes": case.notes,
        "categories": case.categories,
        "comparison": comparison,
        "comparison_notes": mismatch_notes,
        "observations": {
            "cpython": cpython_observation,
            "rebar": rebar_observation,
        },
    }

    if case.text_model is not None:
        result["text_model"] = case.text_model
    if case.pattern is not None:
        result["pattern"] = case.pattern
    if case.flags is not None:
        result["flags"] = case.flags
    if case.helper is not None:
        result["helper"] = case.helper
    if case.args:
        result["args"] = case.serialized_args()
    if case.kwargs:
        result["kwargs"] = case.serialized_kwargs()
    return result


def build_summary(case_results: list[dict[str, Any]]) -> dict[str, int]:
    comparison_counts = {"pass": 0, "fail": 0, "unimplemented": 0, "skipped": 0}
    for result in case_results:
        comparison_counts[result["comparison"]] += 1

    return {
        "total_cases": len(case_results),
        "executed_cases": len(case_results),
        "passed_cases": comparison_counts["pass"],
        "failed_cases": comparison_counts["fail"],
        "unimplemented_cases": comparison_counts["unimplemented"],
        "skipped_cases": comparison_counts["skipped"],
    }


def build_observation_summary(observations: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    warning_categories: dict[str, int] = {}
    exception_types: dict[str, int] = {}
    warning_case_count = 0
    exception_case_count = 0

    for observation in observations:
        outcome = str(observation["outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

        warnings_payload = observation.get("warnings", [])
        if warnings_payload:
            warning_case_count += 1
            for warning_record in warnings_payload:
                category = str(warning_record["category"])
                warning_categories[category] = warning_categories.get(category, 0) + 1

        exception = observation.get("exception")
        if exception is not None:
            exception_case_count += 1
            exception_type = str(exception["type"])
            exception_types[exception_type] = exception_types.get(exception_type, 0) + 1

    return {
        "outcomes": dict(sorted(outcomes.items())),
        "warning_case_count": warning_case_count,
        "exception_case_count": exception_case_count,
        "warning_categories": dict(sorted(warning_categories.items())),
        "exception_types": dict(sorted(exception_types.items())),
    }


def build_diagnostics_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_adapter": {
            "cpython": build_observation_summary(
                [result["observations"]["cpython"] for result in case_results]
            ),
            "rebar": build_observation_summary(
                [result["observations"]["rebar"] for result in case_results]
            ),
        }
    }


def _sorted_unique_strings(values: Iterable[Any]) -> list[str]:
    return sorted({str(value) for value in values if value is not None})


def build_suite_summary(
    *,
    suite_id: str,
    layer: str,
    manifest_ids: list[str],
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": suite_id,
        "layer": layer,
        "manifest_ids": manifest_ids,
        "case_count": len(case_results),
        "families": _sorted_unique_strings(result["family"] for result in case_results),
        "operations": _sorted_unique_strings(result["operation"] for result in case_results),
        "text_models": _sorted_unique_strings(result.get("text_model") for result in case_results),
        "summary": build_summary(case_results),
        "diagnostics": build_diagnostics_summary(case_results),
    }


def build_layer_summaries(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    layers: dict[str, Any] = {}
    for layer in _sorted_unique_strings(result["layer"] for result in case_results):
        layer_cases = [result for result in case_results if result["layer"] == layer]
        layers[layer] = {
            "manifest_ids": _sorted_unique_strings(result["manifest_id"] for result in layer_cases),
            "suite_ids": _sorted_unique_strings(result["suite_id"] for result in layer_cases),
            "case_count": len(layer_cases),
            "families": _sorted_unique_strings(result["family"] for result in layer_cases),
            "operations": _sorted_unique_strings(result["operation"] for result in layer_cases),
            "text_models": _sorted_unique_strings(result.get("text_model") for result in layer_cases),
            "summary": build_summary(layer_cases),
            "diagnostics": build_diagnostics_summary(layer_cases),
        }
    return layers


def build_family_summaries(case_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families = _sorted_unique_strings(result["family"] for result in case_results)
    return [
        {
            "id": family,
            "case_count": len(
                [result for result in case_results if result["family"] == family]
            ),
            "layers": _sorted_unique_strings(
                result["layer"] for result in case_results if result["family"] == family
            ),
            "operations": _sorted_unique_strings(
                result["operation"] for result in case_results if result["family"] == family
            ),
            "text_models": _sorted_unique_strings(
                result.get("text_model") for result in case_results if result["family"] == family
            ),
            "summary": build_summary(
                [result for result in case_results if result["family"] == family]
            ),
        }
        for family in families
    ]


def determine_phase(layer_summaries: dict[str, Any]) -> str:
    active_layers = [layer for layer in PHASE_ORDER if layer in layer_summaries]
    if not active_layers:
        return PHASE_BY_LAYER["parser_acceptance_and_diagnostics"]
    return PHASE_BY_LAYER[active_layers[-1]]


def build_fixture_summary(manifests: Sequence[FixtureManifest], case_results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "manifest_count": len(manifests),
        "manifest_ids": [manifest.manifest_id for manifest in manifests],
        "paths": [str(manifest.path.relative_to(REPO_ROOT)) for manifest in manifests],
        "case_count": len(case_results),
    }
    if len(manifests) == 1:
        manifest = manifests[0]
        summary.update(
            {
                "path": str(manifest.path.relative_to(REPO_ROOT)),
                "schema_version": manifest.schema_version,
                "manifest_id": manifest.manifest_id,
            }
        )
    return summary


def build_suite_summaries(
    manifests: Sequence[FixtureManifest], case_results: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    suite_summaries: list[dict[str, Any]] = []
    for manifest in manifests:
        manifest_cases = [result for result in case_results if result["manifest_id"] == manifest.manifest_id]
        if not manifest_cases:
            continue

        suite_summaries.append(
            build_suite_summary(
                suite_id=manifest.suite_id,
                layer=manifest.layer,
                manifest_ids=[manifest.manifest_id],
                case_results=manifest_cases,
            )
        )

        text_models = _sorted_unique_strings(result.get("text_model") for result in manifest_cases)
        for text_model in text_models:
            suite_summaries.append(
                build_suite_summary(
                    suite_id=f"{manifest.suite_id}.{text_model}",
                    layer=manifest.layer,
                    manifest_ids=[manifest.manifest_id],
                    case_results=[
                        result for result in manifest_cases if result.get("text_model") == text_model
                    ],
                )
            )

        operations = _sorted_unique_strings(result["operation"] for result in manifest_cases)
        if len(operations) > 1:
            for operation in operations:
                suite_summaries.append(
                    build_suite_summary(
                        suite_id=f"{manifest.suite_id}.{operation}",
                        layer=manifest.layer,
                        manifest_ids=[manifest.manifest_id],
                        case_results=[
                            result for result in manifest_cases if result["operation"] == operation
                        ],
                    )
                )

    return suite_summaries


def build_scorecard(
    *,
    manifests: Sequence[FixtureManifest],
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = build_summary(case_results)
    layers = build_layer_summaries(case_results)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "suite": "correctness",
        "phase": determine_phase(layers),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "generator": "python -m rebar_harness.correctness",
        "baseline": {
            **build_cpython_baseline(version_family=TARGET_CPYTHON_SERIES),
            "oracle": "cpython-stdlib-re",
            "target_module": "rebar",
        },
        "fixtures": build_fixture_summary(manifests, case_results),
        "summary": summary,
        "layers": layers,
        "diagnostics": build_diagnostics_summary(case_results),
        "suites": build_suite_summaries(manifests, case_results),
        "families": build_family_summaries(case_results),
        "cases": case_results,
    }


def write_scorecard(scorecard: dict[str, Any], report_path: pathlib.Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_correctness_harness(
    fixture_paths: Sequence[pathlib.Path] = DEFAULT_FIXTURE_PATHS,
    report_path: pathlib.Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    resolved_fixture_paths = [path.resolve() for path in fixture_paths]
    report_path = report_path.resolve()
    manifests, cases = load_fixture_manifests(resolved_fixture_paths)
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()
    case_results = [evaluate_case(case, cpython_adapter, rebar_adapter) for case in cases]
    scorecard = build_scorecard(manifests=manifests, case_results=case_results)
    write_scorecard(scorecard, report_path)
    return scorecard


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures",
        type=pathlib.Path,
        nargs="+",
        default=list(DEFAULT_FIXTURE_PATHS),
        help="One or more correctness fixture manifests to execute.",
    )
    parser.add_argument(
        "--report",
        type=pathlib.Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to the output JSON scorecard.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scorecard = run_correctness_harness(fixture_paths=args.fixtures, report_path=args.report)
    print(json.dumps(scorecard["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
