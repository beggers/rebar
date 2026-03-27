from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import fields, replace
import json
import pathlib
import re
import textwrap
from types import SimpleNamespace

import pytest

import rebar
from rebar_harness import correctness
from rebar_harness.correctness import (
    CORRECTNESS_FIXTURES_ROOT,
    DEFAULT_FIXTURE_PATHS,
    FixtureCase,
    FixtureManifest,
    PARSER_PARITY_FIXTURE_SELECTOR,
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    PUBLIC_SURFACE_FIXTURE_SELECTOR,
    load_fixture_manifest,
    load_fixture_manifests,
    published_fixture_manifests,
    select_correctness_fixture_paths,
)
from rebar_harness.scorecard_io import (
    ordered_published_subset_filenames,
)
from tests.conftest import (
    assert_declared_string_selector_registry_contract,
    assert_published_manifest_inventory_contract,
    assert_published_manifest_helper_contract,
    assert_published_manifest_helper_reload_contract,
    assert_published_selector_subset_paths_contract,
    declared_string_constants_by_suffix,
    records_by_string_id,
)
import tests.python.fixture_parity_support as fixture_parity_support
from tests.python.fixture_parity_support import (
    BoundedPatternCase,
    FixtureBundle,
    PatternTraceCase,
    SupplementalCase,
    assert_bounded_pattern_case_match_parity,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_case_optional_match_parity,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_finditer_parity,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_mixed_text_model_case_pairs,
    assert_pattern_parity,
    assert_value_parity,
    assert_valid_match_group_access_parity,
    bundle_manifest_pytest_id,
    build_selected_fixture_bundle,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    compile_with_cpython_parity,
    flatten_fixture_bundles,
    fixture_bundle_manifest_pytest_id,
    fixture_case_pytest_id,
    fixture_cases_by_id,
    fixture_cases_for_operation,
    follow_on_pytest_id,
    id_attribute_pytest_id,
    invoke_bounded_pattern_case,
    load_single_published_fixture_bundle,
    ordered_fixture_bundle_case_ids,
    str_case_pattern,
    workflow_result_with_cpython_parity,
)
OPTIONAL_NAMED_GROUP_PATTERN = r"a(?P<word>b)?d"
OPTIONAL_NAMED_GROUP_BYTES_PATTERN = rb"a(?P<word>b)?d"
BYTES_LITERAL_PATTERN = b"abc"


class _NonCachingStdlibBackend:
    @staticmethod
    def compile(
        pattern: str | bytes,
        flags: int = 0,
    ) -> re.Pattern[str] | re.Pattern[bytes]:
        re.purge()
        return re.compile(pattern, flags)


class _RecordingNativeBoundaryDispatchContract(
    fixture_parity_support.RecordingNativeBoundary
):
    def __init__(self) -> None:
        super().__init__()
        self.handler_calls: list[tuple[str, tuple[object, ...]]] = []

    def _record(self, handler_name: str, *args: object) -> tuple[str, tuple[object, ...]]:
        payload = (handler_name, args)
        self.handler_calls.append(payload)
        return payload

    def compile_result(self, pattern: str | bytes, flags: int) -> tuple[str, tuple[object, ...]]:
        return self._record("compile_result", pattern, flags)

    def literal_match_result(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, tuple[object, ...]]:
        return self._record(
            "literal_match_result",
            pattern,
            flags,
            mode,
            string,
            pos,
            endpos,
        )

    def literal_split_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        maxsplit: int,
    ) -> tuple[str, tuple[object, ...]]:
        return self._record("literal_split_result", pattern, flags, string, maxsplit)

    def literal_findall_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, tuple[object, ...]]:
        return self._record(
            "literal_findall_result",
            pattern,
            flags,
            string,
            pos,
            endpos,
        )

    def literal_finditer_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, tuple[object, ...]]:
        return self._record(
            "literal_finditer_result",
            pattern,
            flags,
            string,
            pos,
            endpos,
        )

    def literal_subn_result(
        self,
        pattern: str | bytes,
        flags: int,
        repl: str | bytes,
        string: str | bytes,
        count: int,
    ) -> tuple[str, tuple[object, ...]]:
        return self._record(
            "literal_subn_result",
            pattern,
            flags,
            repl,
            string,
            count,
        )

    def escape_result(self, pattern: str | bytes) -> tuple[str, tuple[object, ...]]:
        return self._record("escape_result", pattern)


class _RecordingNativeBoundaryRaisingContract(fixture_parity_support.RecordingNativeBoundary):
    def compile_result(self, pattern: str | bytes, flags: int) -> object:
        raise RuntimeError(f"compile boom for {pattern!r} at flags={flags}")


def _assert_json_literal_safe(value: object) -> None:
    if value is None or isinstance(value, (bool, int, float, str)):
        return
    if isinstance(value, list):
        for item in value:
            _assert_json_literal_safe(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str)
            _assert_json_literal_safe(item)
        return
    raise AssertionError(f"unexpected non-JSON-literal payload {value!r}")


def _payload_type_markers(value: object) -> Counter[str]:
    markers: Counter[str] = Counter()
    if isinstance(value, list):
        for item in value:
            markers.update(_payload_type_markers(item))
        return markers
    if isinstance(value, dict):
        if set(value) == {"encoding", "value"} and all(
            isinstance(value[key], str) for key in ("encoding", "value")
        ):
            markers["normalized-bytes"] += 1
        marker = value.get("type")
        if isinstance(marker, str):
            markers[marker] += 1
        for item in value.values():
            markers.update(_payload_type_markers(item))
    return markers


@pytest.mark.parametrize(
    ("method_name", "call_args", "expected_recorded_call", "expected_handler_name"),
    (
        pytest.param(
            "boundary_compile",
            ("abc", 4),
            ("compile", "abc", 4),
            "compile_result",
            id="compile",
        ),
        pytest.param(
            "boundary_literal_match",
            (b"abc", 2, "search", b"zabc", 1, 5),
            ("match", b"abc", 2, "search", b"zabc", 1, 5),
            "literal_match_result",
            id="literal-match",
        ),
        pytest.param(
            "boundary_literal_split",
            ("abc", 0, "zabc", 3),
            ("split", "abc", 0, "zabc", 3),
            "literal_split_result",
            id="literal-split",
        ),
        pytest.param(
            "boundary_literal_findall",
            (b"abc", 0, b"zabc", 0, None),
            ("findall", b"abc", 0, b"zabc", 0, None),
            "literal_findall_result",
            id="literal-findall",
        ),
        pytest.param(
            "boundary_literal_finditer",
            ("abc", 8, "zabc", 2, None),
            ("finditer", "abc", 8, "zabc", 2, None),
            "literal_finditer_result",
            id="literal-finditer",
        ),
        pytest.param(
            "boundary_literal_subn",
            (b"abc", 0, b"x", b"zabc", 2),
            ("subn", b"abc", 0, b"x", b"zabc", 2),
            "literal_subn_result",
            id="literal-subn",
        ),
        pytest.param(
            "boundary_escape",
            (b"a-b",),
            ("escape", b"a-b"),
            "escape_result",
            id="escape",
        ),
    ),
)
def test_recording_native_boundary_dispatches_to_expected_handler_and_records_calls(
    method_name: str,
    call_args: tuple[object, ...],
    expected_recorded_call: tuple[object, ...],
    expected_handler_name: str,
) -> None:
    boundary = _RecordingNativeBoundaryDispatchContract()

    observed = getattr(boundary, method_name)(*call_args)

    assert observed == (expected_handler_name, call_args)
    assert boundary.calls == [expected_recorded_call]
    assert boundary.handler_calls == [(expected_handler_name, call_args)]


def test_recording_native_boundary_preserves_recorded_call_when_handler_raises() -> None:
    boundary = _RecordingNativeBoundaryRaisingContract()

    with pytest.raises(RuntimeError, match=r"compile boom for 'abc' at flags=7"):
        boundary.boundary_compile("abc", 7)

    assert boundary.calls == [("compile", "abc", 7)]


def test_recording_native_boundary_scaffold_helpers_follow_selected_message_source(
) -> None:
    boundary = fixture_parity_support.RecordingNativeBoundary()

    with pytest.raises(NotImplementedError) as helper_raised:
        boundary.scaffold_raise("search")
    with pytest.raises(NotImplementedError) as pattern_raised:
        boundary.scaffold_pattern_raise("finditer")

    assert helper_raised.value.args == (rebar._placeholder_message("search"),)
    assert pattern_raised.value.args == (
        rebar._pattern_placeholder_message("finditer"),
    )

    native_boundary = fixture_parity_support.RecordingNativeBoundary(
        native_placeholder_messages=True
    )
    with pytest.raises(NotImplementedError, match="native helper placeholder search"):
        native_boundary.scaffold_raise("search")
    with pytest.raises(NotImplementedError, match="native pattern placeholder finditer"):
        native_boundary.scaffold_pattern_raise("finditer")

    native_boundary.scaffold_purge()
    assert native_boundary.calls == [("purge",)]


def test_wrap_candidate_core_texts_preserves_wrapper_pair_order() -> None:
    assert fixture_parity_support.wrap_candidate_core_texts(("ac", "abc")) == (
        "ac",
        "zzac",
        "aczz",
        "zzaczz",
        "abc",
        "zzabc",
        "abczz",
        "zzabczz",
    )


def test_build_wrapped_body_candidate_texts_preserves_generated_matrix_shape() -> None:
    assert fixture_parity_support.build_wrapped_body_candidate_texts(
        ("b", "c"),
        range(2),
        ("d",),
    ) == (
        "ad",
        "zzad",
        "adzz",
        "zzadzz",
        "abd",
        "zzabd",
        "abdzz",
        "zzabdzz",
        "acd",
        "zzacd",
        "acdzz",
        "zzacdzz",
    )
    assert fixture_parity_support.build_wrapped_body_candidate_texts(
        ("b",),
        range(2),
        ("", "d"),
    ) == (
        "a",
        "zza",
        "azz",
        "zzazz",
        "ad",
        "zzad",
        "adzz",
        "zzadzz",
        "ab",
        "zzab",
        "abzz",
        "zzabzz",
        "abd",
        "zzabd",
        "abdzz",
        "zzabdzz",
    )


def test_wrapped_candidate_text_helpers_deduplicate_colliding_outputs_in_first_seen_order(
) -> None:
    assert fixture_parity_support.wrap_candidate_core_texts(("", "zz", "")) == (
        "",
        "zz",
        "zzzz",
        "zzzzzz",
    )
    assert fixture_parity_support.build_wrapped_body_candidate_texts(
        ("", "b"),
        range(2),
        ("", "d"),
    ) == (
        "a",
        "zza",
        "azz",
        "zzazz",
        "ad",
        "zzad",
        "adzz",
        "zzadzz",
        "ab",
        "zzab",
        "abzz",
        "zzabzz",
        "abd",
        "zzabd",
        "abdzz",
        "zzabdzz",
    )


def _tracked_fixture_paths() -> tuple[pathlib.Path, ...]:
    return tuple(
        sorted(CORRECTNESS_FIXTURES_ROOT.glob("*.py"), key=lambda path: path.name)
    )


def _write_fixture_module(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


BUNDLE_LOADER_CONTRACT_STR_FILENAME = "bundle_loader_contract_str.py"
BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID = "bundle-loader-contract-str"
BUNDLE_LOADER_CONTRACT_MIXED_FILENAME = "bundle_loader_contract_mixed.py"
BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID = "bundle-loader-contract-mixed"
BUNDLE_LOADER_CONTRACT_DUPLICATE_FILENAME = "bundle_loader_contract_duplicate.py"
BUNDLE_LOADER_CONTRACT_DUPLICATE_MANIFEST_ID = "bundle-loader-contract-duplicate"
BUNDLE_LOADER_CONTRACT_DUPLICATE_CASE_ID = "bundle-loader-contract-duplicate-case"
ZERO_FLAG_KEYWORD_CARRIER_FILENAME = "zero_flag_keyword_carrier_contract.py"
ZERO_FLAG_KEYWORD_CARRIER_MANIFEST_ID = "zero-flag-keyword-carrier-contract"
ZERO_FLAG_KEYWORD_NOFLAG_CASE_ID = "zero-flag-keyword-noflag"
ZERO_FLAG_KEYWORD_INT_ZERO_CASE_ID = "zero-flag-keyword-int-zero"
ZERO_FLAG_KEYWORD_BOOL_FALSE_CASE_ID = "zero-flag-keyword-bool-false"


def _write_bundle_loader_contract_fixture_modules(
    tmp_path: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path]:
    str_path = _write_fixture_module(
        tmp_path,
        BUNDLE_LOADER_CONTRACT_STR_FILENAME,
        f"""
        MANIFEST = {{
            "schema_version": 1,
            "manifest_id": "{BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID}",
            "layer": "module_workflow",
            "suite_id": "bundle.loader.contract.str",
            "cases": [
                {{
                    "id": "bundle-loader-contract-compile-str",
                    "operation": "compile",
                    "pattern": r"(?P<word>ab)(?P=word)",
                    "text_model": "str",
                }},
                {{
                    "id": "bundle-loader-contract-module-search-str",
                    "operation": "module_call",
                    "helper": "search",
                    "pattern": r"(?P<word>ab)(?P=word)",
                    "text_model": "str",
                }},
                {{
                    "id": "bundle-loader-contract-pattern-search-str",
                    "operation": "pattern_call",
                    "helper": "search",
                    "pattern": r"(?P<word>ab)(?P=word)",
                    "text_model": "str",
                }},
            ],
        }}
        """,
    )
    mixed_path = _write_fixture_module(
        tmp_path,
        BUNDLE_LOADER_CONTRACT_MIXED_FILENAME,
        f"""
        MANIFEST = {{
            "schema_version": 1,
            "manifest_id": "{BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID}",
            "layer": "module_workflow",
            "suite_id": "bundle.loader.contract.mixed",
            "cases": [
                {{
                    "id": "bundle-loader-contract-mixed-compile-str",
                    "operation": "compile",
                    "pattern": r"a(bc|de){{1,}}d",
                    "text_model": "str",
                }},
                {{
                    "id": "bundle-loader-contract-mixed-module-search-str",
                    "operation": "module_call",
                    "helper": "search",
                    "pattern": r"a(bc|de){{1,}}d",
                    "text_model": "str",
                }},
                {{
                    "id": "bundle-loader-contract-mixed-compile-bytes",
                    "operation": "compile",
                    "pattern": r"a(bc|de){{1,}}d",
                    "text_model": "bytes",
                }},
                {{
                    "id": "bundle-loader-contract-mixed-pattern-fullmatch-bytes",
                    "operation": "pattern_call",
                    "helper": "fullmatch",
                    "pattern": r"a(bc|de){{1,}}d",
                    "text_model": "bytes",
                }},
            ],
        }}
        """,
    )
    return str_path, mixed_path


def _write_bundle_loader_contract_duplicate_fixture_module(
    tmp_path: pathlib.Path,
) -> pathlib.Path:
    return _write_fixture_module(
        tmp_path,
        BUNDLE_LOADER_CONTRACT_DUPLICATE_FILENAME,
        f"""
        MANIFEST = {{
            "schema_version": 1,
            "manifest_id": "{BUNDLE_LOADER_CONTRACT_DUPLICATE_MANIFEST_ID}",
            "layer": "module_workflow",
            "suite_id": "bundle.loader.contract.duplicate",
            "cases": [
                {{
                    "id": "{BUNDLE_LOADER_CONTRACT_DUPLICATE_CASE_ID}",
                    "operation": "compile",
                    "pattern": "abc",
                    "text_model": "str",
                }},
                {{
                    "id": "{BUNDLE_LOADER_CONTRACT_DUPLICATE_CASE_ID}",
                    "operation": "module_call",
                    "helper": "search",
                    "pattern": "abc",
                    "text_model": "str",
                }},
            ],
        }}
        """,
    )


def _write_zero_flag_keyword_carrier_fixture_module(
    tmp_path: pathlib.Path,
) -> pathlib.Path:
    return _write_fixture_module(
        tmp_path,
        ZERO_FLAG_KEYWORD_CARRIER_FILENAME,
        f"""
        import re

        MANIFEST = {{
            "schema_version": 1,
            "manifest_id": "{ZERO_FLAG_KEYWORD_CARRIER_MANIFEST_ID}",
            "layer": "module_workflow",
            "suite_id": "zero.flag.keyword.carrier.contract",
            "cases": [
                {{
                    "id": "{ZERO_FLAG_KEYWORD_NOFLAG_CASE_ID}",
                    "operation": "module_call",
                    "helper": "compile",
                    "pattern": "(?P<word>abc)",
                    "text_model": "str",
                    "use_compiled_pattern": True,
                    "kwargs": {{
                        "flags": re.NOFLAG,
                    }},
                }},
                {{
                    "id": "{ZERO_FLAG_KEYWORD_INT_ZERO_CASE_ID}",
                    "operation": "module_call",
                    "helper": "compile",
                    "pattern": "(?P<word>abc)",
                    "text_model": "str",
                    "use_compiled_pattern": True,
                    "kwargs": {{
                        "flags": 0,
                    }},
                }},
                {{
                    "id": "{ZERO_FLAG_KEYWORD_BOOL_FALSE_CASE_ID}",
                    "operation": "module_call",
                    "helper": "compile",
                    "pattern": "(?P<word>abc)",
                    "text_model": "str",
                    "use_compiled_pattern": True,
                    "kwargs": {{
                        "flags": False,
                    }},
                }},
            ],
        }}
        """,
    )


def _assert_zero_flag_keyword_carrier(
    case: FixtureCase,
    *,
    expected_type: type[object],
) -> None:
    source_value = case.source_kwargs["flags"]
    materialized_value = case.kwargs["flags"]

    assert type(source_value) is expected_type
    assert type(materialized_value) is expected_type
    assert source_value == 0
    assert materialized_value == 0


def _load_full_fixture_bundle(
    fixture_path: pathlib.Path,
    *,
    pattern_extractor: Callable[[FixtureCase], str | bytes] = case_pattern,
) -> FixtureBundle:
    return build_selected_fixture_bundle(
        fixture_path,
        pattern_extractor=pattern_extractor,
    )


def _load_bundle_loader_contract_str_bundle(tmp_path: pathlib.Path) -> FixtureBundle:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    return _load_full_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )


def _load_bundle_loader_contract_mixed_bundle(tmp_path: pathlib.Path) -> FixtureBundle:
    _, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    return _load_full_fixture_bundle(
        mixed_path,
        pattern_extractor=case_pattern,
    )


def _paired_mixed_text_contract_bundle() -> FixtureBundle:
    manifest = FixtureManifest(
        path=pathlib.Path("synthetic_paired_mixed_text_contract.py"),
        manifest_id="synthetic-paired-mixed-text-contract",
        layer="module_workflow",
        suite_id="synthetic.paired.mixed.text.contract",
        schema_version=1,
        defaults={},
        cases=[],
    )
    paired_cases = (
        replace(
            SYNTHETIC_MODULE_PATTERN_CASE,
            case_id="synthetic-mixed-module-search-str",
            manifest_id=manifest.manifest_id,
            suite_id=manifest.suite_id,
            layer=manifest.layer,
            family=manifest.manifest_id,
            categories=["workflow", "search", "literal", "str"],
        ),
        replace(
            SYNTHETIC_COMPILED_PATTERN_CASE,
            case_id="synthetic-mixed-pattern-search-str",
            manifest_id=manifest.manifest_id,
            suite_id=manifest.suite_id,
            layer=manifest.layer,
            family=manifest.manifest_id,
            categories=["workflow", "search", "literal", "str"],
        ),
        replace(
            SYNTHETIC_MODULE_BYTES_SEARCH_CASE,
            case_id="synthetic-mixed-module-search-bytes",
            manifest_id=manifest.manifest_id,
            suite_id=manifest.suite_id,
            layer=manifest.layer,
            family=manifest.manifest_id,
            pattern=SYNTHETIC_CASE_PATTERN,
            source_args=[SYNTHETIC_CASE_PATTERN.encode("latin-1"), b"zzabczz"],
            args=[SYNTHETIC_CASE_PATTERN.encode("latin-1"), b"zzabczz"],
            categories=["workflow", "search", "literal", "bytes"],
        ),
        replace(
            SYNTHETIC_COMPILED_PATTERN_CASE,
            case_id="synthetic-mixed-pattern-search-bytes",
            manifest_id=manifest.manifest_id,
            suite_id=manifest.suite_id,
            layer=manifest.layer,
            family=manifest.manifest_id,
            pattern=SYNTHETIC_CASE_PATTERN,
            text_model="bytes",
            categories=["workflow", "search", "literal", "bytes"],
            source_args=[b"zzabczz"],
            args=[b"zzabczz"],
        ),
    )
    return FixtureBundle(
        manifest=manifest,
        cases=paired_cases,
        expected_patterns=frozenset(case_pattern(case) for case in paired_cases),
        expected_operation_helper_counts=Counter(
            (case.operation, case.helper) for case in paired_cases
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    )


def _normalized_bytes_payload(value: bytes) -> dict[str, str]:
    return {
        "type": "bytes",
        "encoding": "latin-1",
        "value": value.decode("latin-1"),
    }


def test_assert_mixed_text_model_case_pairs_returns_str_and_bytes_rows() -> None:
    bundle = _paired_mixed_text_contract_bundle()

    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)

    assert tuple(case.case_id for case in str_cases) == (
        "synthetic-mixed-module-search-str",
        "synthetic-mixed-pattern-search-str",
    )
    assert tuple(case.case_id for case in bytes_cases) == (
        "synthetic-mixed-module-search-bytes",
        "synthetic-mixed-pattern-search-bytes",
    )


def test_assert_mixed_text_model_case_pairs_accepts_normalized_bytes_payload_rows(
) -> None:
    bundle = _paired_mixed_text_contract_bundle()
    normalized_module_case = replace(
        bundle.cases[2],
        source_args=[
            _normalized_bytes_payload(SYNTHETIC_CASE_PATTERN.encode("latin-1")),
            _normalized_bytes_payload(b"zzabczz"),
        ],
        args=[
            _normalized_bytes_payload(SYNTHETIC_CASE_PATTERN.encode("latin-1")),
            _normalized_bytes_payload(b"zzabczz"),
        ],
    )
    normalized_pattern_case = replace(
        bundle.cases[3],
        source_args=[_normalized_bytes_payload(b"zzabczz")],
        args=[_normalized_bytes_payload(b"zzabczz")],
    )

    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(
        replace(
            bundle,
            cases=(
                bundle.cases[0],
                bundle.cases[1],
                normalized_module_case,
                normalized_pattern_case,
            ),
        )
    )

    assert tuple(case.case_id for case in str_cases) == (
        "synthetic-mixed-module-search-str",
        "synthetic-mixed-pattern-search-str",
    )
    assert tuple(case.case_id for case in bytes_cases) == (
        "synthetic-mixed-module-search-bytes",
        "synthetic-mixed-pattern-search-bytes",
    )


def test_assert_mixed_text_model_case_pairs_accepts_nested_normalized_bytes_payload_rows(
) -> None:
    bundle = _paired_mixed_text_contract_bundle()

    nested_module_str_args = [
        {
            "pattern": SYNTHETIC_CASE_PATTERN,
            "targets": ("zzabczz",),
        }
    ]
    nested_module_bytes_args = [
        {
            "pattern": _normalized_bytes_payload(
                SYNTHETIC_CASE_PATTERN.encode("latin-1")
            ),
            "targets": (_normalized_bytes_payload(b"zzabczz"),),
        }
    ]
    nested_pattern_str_args = [
        (
            "zzabczz",
            {
                "expected": ["abc"],
            },
        )
    ]
    nested_pattern_bytes_args = [
        (
            _normalized_bytes_payload(b"zzabczz"),
            {
                "expected": [_normalized_bytes_payload(b"abc")],
            },
        )
    ]

    nested_bundle = replace(
        bundle,
        cases=(
            replace(
                bundle.cases[0],
                source_args=nested_module_str_args,
                args=nested_module_str_args,
            ),
            replace(
                bundle.cases[1],
                source_args=nested_pattern_str_args,
                args=nested_pattern_str_args,
            ),
            replace(
                bundle.cases[2],
                source_args=nested_module_bytes_args,
                args=nested_module_bytes_args,
            ),
            replace(
                bundle.cases[3],
                source_args=nested_pattern_bytes_args,
                args=nested_pattern_bytes_args,
            ),
        ),
    )

    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(nested_bundle)

    assert tuple(case.case_id for case in str_cases) == (
        "synthetic-mixed-module-search-str",
        "synthetic-mixed-pattern-search-str",
    )
    assert tuple(case.case_id for case in bytes_cases) == (
        "synthetic-mixed-module-search-bytes",
        "synthetic-mixed-pattern-search-bytes",
    )


@pytest.mark.parametrize(
    ("drift_kind", "expected_message"),
    (
        pytest.param(
            "missing-bytes",
            "mixed-text-model contract requires str/bytes rows",
            id="missing-bytes",
        ),
        pytest.param(
            "row-count",
            "mixed-text-model rows drifted",
            id="row-count",
        ),
        pytest.param(
            "case-id-pairing",
            "mixed-text-model case id pairing drifted",
            id="case-id-pairing",
        ),
    ),
)
def test_assert_mixed_text_model_case_pairs_rejects_pairing_drift(
    drift_kind: str,
    expected_message: str,
) -> None:
    bundle = _paired_mixed_text_contract_bundle()

    if drift_kind == "missing-bytes":
        drifted_bundle = replace(bundle, cases=bundle.cases[:2])
    elif drift_kind == "row-count":
        drifted_bundle = replace(bundle, cases=bundle.cases[:-1])
    elif drift_kind == "case-id-pairing":
        drifted_bundle = replace(
            bundle,
            cases=(
                bundle.cases[0],
                bundle.cases[1],
                replace(
                    bundle.cases[2],
                    case_id="synthetic-mixed-module-search-unpaired-bytes",
                ),
                bundle.cases[3],
            ),
        )
    else:
        raise AssertionError(f"unexpected drift_kind {drift_kind!r}")

    with pytest.raises(AssertionError, match=re.escape(expected_message)):
        assert_mixed_text_model_case_pairs(drifted_bundle)


@pytest.mark.parametrize(
    ("drift_kwargs", "expected_message"),
    (
        pytest.param(
            {"operation": "pattern_call"},
            "operation drifted",
            id="operation",
        ),
        pytest.param(
            {"helper": "fullmatch"},
            "helper drifted",
            id="helper",
        ),
        pytest.param(
            {"family": "synthetic-mixed-family-drift"},
            "family drifted",
            id="family",
        ),
        pytest.param(
            {"pattern": "abd"},
            "pattern drifted",
            id="pattern",
        ),
        pytest.param(
            {"flags": re.IGNORECASE},
            "flags drifted",
            id="flags",
        ),
        pytest.param(
            {"pattern_encoding": "utf-8"},
            "pattern encoding drifted",
            id="pattern-encoding",
        ),
        pytest.param(
            {"use_compiled_pattern": True},
            "compiled-pattern routing drifted",
            id="compiled-pattern-routing",
        ),
        pytest.param(
            {"include_pattern_arg": True},
            "include-pattern routing drifted",
            id="include-pattern-routing",
        ),
        pytest.param(
            {"source_args": [rb"(?P<word>abc)", b"zzabdzz"]},
            "source args drifted",
            id="source-args",
        ),
        pytest.param(
            {"args": [rb"(?P<word>abc)", b"zzabdzz"]},
            "args drifted",
            id="args",
        ),
        pytest.param(
            {"kwargs": {"pos": 1}},
            "kwargs drifted",
            id="kwargs",
        ),
        pytest.param(
            {"source_kwargs": {"pos": 1}},
            "source kwargs drifted",
            id="source-kwargs",
        ),
        pytest.param(
            {"categories": ["workflow", "search", "capturing", "bytes"]},
            "categories drifted",
            id="categories",
        ),
    ),
)
def test_assert_mixed_text_model_case_pairs_rejects_structural_drift(
    drift_kwargs: dict[str, object],
    expected_message: str,
) -> None:
    bundle = _paired_mixed_text_contract_bundle()
    drifted_bytes_case = replace(
        bundle.cases[2],
        **drift_kwargs,
    )
    drifted_bundle = replace(
        bundle,
        cases=(
            bundle.cases[0],
            bundle.cases[1],
            drifted_bytes_case,
            bundle.cases[3],
        ),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(expected_message),
    ):
        assert_mixed_text_model_case_pairs(drifted_bundle)
SYNTHETIC_CASE_PATTERN = r"(?P<word>abc)"
SYNTHETIC_PATTERN_HELPER_CASE = FixtureCase(
    case_id="synthetic-pattern-helper-case",
    manifest_id="synthetic-pattern-helper-contract",
    suite_id="synthetic-pattern-helper-contract",
    layer="pattern_helper_contracts",
    family="fixture_support_contracts",
    operation="compile",
    notes=[],
    categories=[],
    pattern=SYNTHETIC_CASE_PATTERN,
    flags=None,
    text_model="str",
    pattern_encoding="latin-1",
    helper=None,
    source_args=[],
    source_kwargs={},
    args=[],
    kwargs={},
)
SYNTHETIC_MODULE_PATTERN_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-module-pattern-str",
    operation="module_call",
    helper="search",
    source_args=[SYNTHETIC_CASE_PATTERN, "zzabczz"],
    args=[SYNTHETIC_CASE_PATTERN, "zzabczz"],
)
SYNTHETIC_COMPILED_MODULE_PATTERN_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-module-compiled-pattern-str",
    operation="module_call",
    helper="search",
    source_args=["zzabczz"],
    args=["zzabczz"],
    use_compiled_pattern=True,
)
SYNTHETIC_COMPILED_PATTERN_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-pattern-pattern-str",
    operation="pattern_call",
    helper="search",
    source_args=["zzabczz"],
    args=["zzabczz"],
)
SYNTHETIC_MODULE_BYTES_SEARCH_CASE = replace(
    SYNTHETIC_MODULE_PATTERN_CASE,
    case_id="synthetic-module-pattern-bytes",
    pattern="abc",
    text_model="bytes",
    source_args=[b"abc", b"zzabczz"],
    args=[b"abc", b"zzabczz"],
)
SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE = replace(
    SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
    case_id="synthetic-module-compiled-pattern-bytes",
    pattern="abc",
    text_model="bytes",
    source_args=[b"zzabczz"],
    args=[b"zzabczz"],
)
SYNTHETIC_INCLUDE_PATTERN_MODULE_KEYWORD_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-module-pattern-keyword-str",
    operation="module_call",
    helper="search",
    pattern="abc",
    source_args=["zzABCzz"],
    source_kwargs={"flags": int(re.IGNORECASE)},
    args=["zzABCzz"],
    kwargs={"flags": int(re.IGNORECASE)},
    include_pattern_arg=True,
)
SYNTHETIC_COMPILED_MODULE_KEYWORD_SPLIT_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-module-compiled-pattern-keyword-split-str",
    operation="module_call",
    helper="split",
    pattern="abc",
    source_args=["abcabcabc"],
    source_kwargs={"maxsplit": 1},
    args=["abcabcabc"],
    kwargs={"maxsplit": 1},
    use_compiled_pattern=True,
)
SYNTHETIC_COMPILED_MODULE_COMPILE_CASE = replace(
    SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
    case_id="synthetic-module-compiled-pattern-compile-str",
    helper="compile",
    source_args=[],
    args=[],
)
SYNTHETIC_COMPILED_MODULE_COMPILE_INT_ZERO_CASE = replace(
    SYNTHETIC_COMPILED_MODULE_COMPILE_CASE,
    case_id="synthetic-module-compiled-pattern-compile-int-zero-str",
    source_kwargs={"flags": 0},
    kwargs={"flags": 0},
)
SYNTHETIC_COMPILED_MODULE_COMPILE_BOOL_FALSE_CASE = replace(
    SYNTHETIC_COMPILED_MODULE_COMPILE_CASE,
    case_id="synthetic-module-compiled-pattern-compile-bool-false-str",
    source_kwargs={"flags": False},
    kwargs={"flags": False},
)
SYNTHETIC_COMPILED_MODULE_BYTES_COMPILE_CASE = replace(
    SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
    case_id="synthetic-module-compiled-pattern-compile-bytes",
    helper="compile",
    source_args=[],
    args=[],
)
SYNTHETIC_FULLMATCH_PATTERN_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-pattern-fullmatch-str",
    operation="pattern_call",
    helper="fullmatch",
    source_args=["abc"],
    args=["abc"],
)
SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE = replace(
    SYNTHETIC_FULLMATCH_PATTERN_CASE,
    case_id="synthetic-pattern-fullmatch-bytes",
    pattern="abc",
    text_model="bytes",
    source_args=[b"abc"],
    args=[b"abc"],
)
SYNTHETIC_BYTES_PATTERN_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-pattern-bytes",
    operation="pattern_call",
    pattern="abc",
    text_model="bytes",
    helper="split",
    source_args=[b"zzabczz", 1],
    args=[b"zzabczz", 1],
)
SYNTHETIC_PATTERN_KEYWORD_SEARCH_CASE = replace(
    SYNTHETIC_PATTERN_HELPER_CASE,
    case_id="synthetic-pattern-search-keyword-str",
    operation="pattern_call",
    helper="search",
    pattern="abc",
    source_args=["abcxabc"],
    source_kwargs={"pos": 4, "endpos": 7},
    args=["abcxabc"],
    kwargs={"pos": 4, "endpos": 7},
)
BRANCH_LOCAL_NAMED_BACKREFERENCE_PATTERN = (
    r"a(?P<outer>(?P<inner>bc)|de)(?P=inner)d"
)
BRANCH_LOCAL_NAMED_BACKREFERENCE_SEARCH_TEXT = "zzabcbcdzz"
BRANCH_LOCAL_NAMED_BACKREFERENCE_FULLMATCH_TEXT = "abcbcd"
BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_PATTERN = (
    rb"a(?P<outer>(?P<inner>bc)|de)(?P=inner)d"
)
BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_SEARCH_TEXT = b"zzabcbcdzz"
BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_FULLMATCH_TEXT = b"abcbcd"


def _optional_named_group_match(
    backend_name: str,
    backend: object,
    text: str,
    *,
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[str] | None]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            OPTIONAL_NAMED_GROUP_PATTERN,
        )
        return (
            observed_pattern.fullmatch(text),
            expected_pattern.fullmatch(text),
        )

    return (
        backend.fullmatch(OPTIONAL_NAMED_GROUP_PATTERN, text),
        re.fullmatch(OPTIONAL_NAMED_GROUP_PATTERN, text),
    )


def _optional_named_group_bytes_match(
    backend_name: str,
    backend: object,
    text: bytes,
    *,
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[bytes] | None]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            OPTIONAL_NAMED_GROUP_BYTES_PATTERN,
        )
        return (
            observed_pattern.fullmatch(text),
            expected_pattern.fullmatch(text),
        )

    return (
        backend.fullmatch(OPTIONAL_NAMED_GROUP_BYTES_PATTERN, text),
        re.fullmatch(OPTIONAL_NAMED_GROUP_BYTES_PATTERN, text),
    )


def _bytes_literal_search_match(
    backend_name: str,
    backend: object,
    text: bytes,
    *,
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[bytes] | None]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            BYTES_LITERAL_PATTERN,
        )
        return (
            observed_pattern.search(text),
            expected_pattern.search(text),
        )

    return (
        backend.search(BYTES_LITERAL_PATTERN, text),
        re.search(BYTES_LITERAL_PATTERN, text),
    )


def _str_literal_search_match(
    backend_name: str,
    backend: object,
    text: str,
    *,
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[str] | None]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            "abc",
        )
        return (
            observed_pattern.search(text),
            expected_pattern.search(text),
        )

    return (
        backend.search("abc", text),
        re.search("abc", text),
    )


def _branch_local_named_backreference_match(
    backend_name: str,
    backend: object,
    *,
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[str] | None]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            BRANCH_LOCAL_NAMED_BACKREFERENCE_PATTERN,
        )
        return (
            observed_pattern.fullmatch(BRANCH_LOCAL_NAMED_BACKREFERENCE_FULLMATCH_TEXT),
            expected_pattern.fullmatch(BRANCH_LOCAL_NAMED_BACKREFERENCE_FULLMATCH_TEXT),
        )

    return (
        backend.search(
            BRANCH_LOCAL_NAMED_BACKREFERENCE_PATTERN,
            BRANCH_LOCAL_NAMED_BACKREFERENCE_SEARCH_TEXT,
        ),
        re.search(
            BRANCH_LOCAL_NAMED_BACKREFERENCE_PATTERN,
            BRANCH_LOCAL_NAMED_BACKREFERENCE_SEARCH_TEXT,
        ),
    )


def _branch_local_named_backreference_bytes_match(
    backend_name: str,
    backend: object,
    *,
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[bytes] | None]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_PATTERN,
        )
        return (
            observed_pattern.fullmatch(
                BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_FULLMATCH_TEXT
            ),
            expected_pattern.fullmatch(
                BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_FULLMATCH_TEXT
            ),
        )

    return (
        backend.search(
            BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_PATTERN,
            BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_SEARCH_TEXT,
        ),
        re.search(
            BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_PATTERN,
            BRANCH_LOCAL_NAMED_BACKREFERENCE_BYTES_SEARCH_TEXT,
        ),
    )


def _expand_match(
    backend_name: str,
    backend: object,
    pattern: str | bytes,
    text: str | bytes,
    *,
    helper: str = "search",
    use_compiled_pattern: bool,
) -> tuple[object, re.Match[str] | re.Match[bytes]]:
    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed_match = getattr(observed_pattern, helper)(text)
        expected_match = getattr(expected_pattern, helper)(text)
    else:
        observed_match = getattr(backend, helper)(pattern, text)
        expected_match = getattr(re, helper)(pattern, text)

    assert observed_match is not None
    assert expected_match is not None
    return observed_match, expected_match


def _capture_expand_error(match: object, template: object) -> BaseException:
    try:
        match.expand(template)
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError("expected match.expand() to raise")


@pytest.mark.parametrize(
    "selector",
    tuple(
        sorted(correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES)
    ),
)
def test_shared_correctness_fixture_selectors_resolve_published_paths(
    selector: str,
) -> None:
    published_full_suite_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    resolved_paths = select_correctness_fixture_paths(selector)

    assert_published_selector_subset_paths_contract(
        published_full_suite_paths,
        resolved_paths,
        root_path=CORRECTNESS_FIXTURES_ROOT,
        expected_filenames=correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector],
    )


@pytest.mark.parametrize(
    "selector",
    (
        PARSER_PARITY_FIXTURE_SELECTOR,
        PUBLIC_SURFACE_FIXTURE_SELECTOR,
    ),
)
def test_canonical_published_subset_selectors_keep_explicit_membership_contract(
    selector: str,
) -> None:
    expected_filenames = (
        correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES[
            selector
        ]
    )
    assert correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector] == (
        expected_filenames
    )

    assert_published_selector_subset_paths_contract(
        select_correctness_fixture_paths(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR),
        select_correctness_fixture_paths(selector),
        root_path=CORRECTNESS_FIXTURES_ROOT,
        expected_filenames=expected_filenames,
    )


def test_correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "unknown published correctness fixture filename(s): ['missing_fixture.py']"
        ),
    ):
        ordered_published_subset_filenames(
            correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[
                PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
            ],
            ("missing_fixture.py",),
            missing_filename_error_prefix=(
                correctness._PUBLISHED_CORRECTNESS_FIXTURE_MISSING_ERROR_PREFIX
            ),
        )


def test_unknown_correctness_fixture_selector_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="unknown correctness fixture selector"):
        select_correctness_fixture_paths("missing-selector")


def test_declared_correctness_fixture_selectors_match_registry_keys() -> None:
    declared_selectors = assert_declared_string_selector_registry_contract(
        correctness,
        name_suffix="_FIXTURE_SELECTOR",
        selector_registry=correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR,
    )

    assert declared_selectors


def test_declared_nondefault_correctness_fixture_selectors_are_parametrized_once() -> None:
    declared_nondefault_selectors = tuple(
        sorted(
            selector
            for selector in declared_string_constants_by_suffix(
                correctness,
                name_suffix="_FIXTURE_SELECTOR",
            ).values()
            if selector != PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
        )
    )
    expected_selectors = tuple(
        sorted(correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES)
    )

    assert PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR not in expected_selectors
    assert len(expected_selectors) == len(set(expected_selectors))
    assert expected_selectors == declared_nondefault_selectors


def test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory() -> None:
    published_fixture_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    tracked_fixture_paths = _tracked_fixture_paths()

    assert DEFAULT_FIXTURE_PATHS == published_fixture_paths
    assert set(published_fixture_paths) == set(tracked_fixture_paths)
    assert len(published_fixture_paths) == len(set(published_fixture_paths))

    for path in published_fixture_paths:
        assert path.is_relative_to(CORRECTNESS_FIXTURES_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"


def test_published_full_suite_fixture_selector_preserves_explicit_manifest_order() -> None:
    published_fixture_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )

    assert tuple(path.name for path in published_fixture_paths) == tuple(
        path.name for path in DEFAULT_FIXTURE_PATHS
    )


def test_case_pattern_helpers_extract_str_and_bytes_patterns_from_synthetic_fixture_cases() -> None:
    assert case_pattern(SYNTHETIC_MODULE_PATTERN_CASE) == SYNTHETIC_CASE_PATTERN
    assert str_case_pattern(SYNTHETIC_MODULE_PATTERN_CASE) == SYNTHETIC_CASE_PATTERN
    assert case_pattern(SYNTHETIC_COMPILED_PATTERN_CASE) == SYNTHETIC_CASE_PATTERN
    assert str_case_pattern(SYNTHETIC_COMPILED_PATTERN_CASE) == SYNTHETIC_CASE_PATTERN
    assert case_pattern(SYNTHETIC_BYTES_PATTERN_CASE) == b"abc"


def test_case_pattern_helpers_reject_non_text_payloads_and_str_only_mismatches() -> None:
    with pytest.raises(AssertionError):
        case_pattern(
            replace(
                SYNTHETIC_MODULE_PATTERN_CASE,
                pattern=None,
                args=[123, "zzabczz"],
            )
        )

    with pytest.raises(AssertionError):
        str_case_pattern(SYNTHETIC_BYTES_PATTERN_CASE)


def test_indexlike_helper_contract_exposes_value_and_repr() -> None:
    carrier = fixture_parity_support.IndexLike(7)

    assert carrier.__index__() == 7
    assert repr(carrier) == "IndexLike(7)"


def test_recording_indexlike_helper_tracks_each_index_request() -> None:
    carrier = fixture_parity_support.RecordingIndexLike(4)

    assert carrier.calls == 0
    assert carrier.__index__() == 4
    assert carrier.__index__() == 4
    assert carrier.calls == 2


def test_recording_indexlike_helper_propagates_configured_errors_after_counting_calls(
) -> None:
    error = fixture_parity_support.IndexLikeBoomError("indexlike boom")
    carrier = fixture_parity_support.RecordingIndexLike(error=error)

    with pytest.raises(
        fixture_parity_support.IndexLikeBoomError,
        match="indexlike boom",
    ) as raised:
        carrier.__index__()

    assert raised.value is error
    assert carrier.calls == 1


def test_module_workflow_positional_signature_distinguishes_bool_int_and_indexlike() -> None:
    assert fixture_parity_support.module_workflow_positional_args_signature(
        [True, fixture_parity_support.IndexLike(1), 1, "abc", b"abc"]
    ) == (
        ("bool", True),
        ("indexlike", 1),
        ("int", 1),
        ("str", "abc"),
        ("bytes", b"abc"),
    )
    assert fixture_parity_support.module_workflow_positional_args_signature(
        [fixture_parity_support.IndexLike(4)]
    ) == fixture_parity_support.module_workflow_positional_args_signature(
        [{"type": "indexlike", "value": 4}]
    )


def test_module_workflow_keyword_signature_preserves_explicit_noflag() -> None:
    assert fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"flags": re.NOFLAG}
    ) == (("flags", "regexflag", 0),)
    assert fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"flags": re.NOFLAG}
    ) != fixture_parity_support.module_workflow_keyword_kwargs_signature({"flags": 0})
    assert fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"flags": re.NOFLAG}
    ) != fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"flags": False}
    )


def test_module_workflow_keyword_signature_accepts_encoded_indexlike_payloads() -> None:
    assert fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"endpos": {"type": "indexlike", "value": 4}}
    ) == fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"endpos": fixture_parity_support.IndexLike(4)}
    )


def test_module_workflow_positional_signature_rejects_bool_encoded_indexlike_payloads() -> None:
    assert fixture_parity_support.module_workflow_positional_args_signature(
        [{"type": "indexlike", "value": True}]
    ) == (("dict", "{'type': 'indexlike', 'value': True}"),)


def test_module_workflow_keyword_signature_rejects_bool_encoded_indexlike_payloads() -> None:
    assert fixture_parity_support.module_workflow_keyword_kwargs_signature(
        {"endpos": {"type": "indexlike", "value": True}}
    ) == (("endpos", "dict", "{'type': 'indexlike', 'value': True}"),)


@pytest.mark.parametrize(
    ("case", "expected_replacement", "expected_text"),
    (
        pytest.param(
            replace(
                SYNTHETIC_MODULE_PATTERN_CASE,
                operation="module_call",
                helper="sub",
                source_args=[SYNTHETIC_CASE_PATTERN, r"<\g<word>>", "abc"],
                args=[SYNTHETIC_CASE_PATTERN, r"<\g<word>>", "abc"],
            ),
            r"<\g<word>>",
            "abc",
            id="module-call",
        ),
        pytest.param(
            replace(
                SYNTHETIC_COMPILED_PATTERN_CASE,
                operation="pattern_call",
                helper="sub",
                source_args=[r"<\g<word>>", "abc"],
                args=[r"<\g<word>>", "abc"],
            ),
            r"<\g<word>>",
            "abc",
            id="pattern-call",
        ),
    ),
)
def test_case_replacement_and_text_helpers_extract_expected_argument_positions(
    case: FixtureCase,
    expected_replacement: object,
    expected_text: str | bytes,
) -> None:
    assert case_replacement_argument(case) == expected_replacement
    assert case_text_argument(case) == expected_text


def test_case_replacement_and_text_helpers_reject_unsupported_case_operations() -> None:
    invalid_case = replace(SYNTHETIC_MODULE_PATTERN_CASE, operation="compile")

    with pytest.raises(AssertionError, match="unsupported case operation 'compile'"):
        case_replacement_argument(invalid_case)

    with pytest.raises(AssertionError, match="unsupported case operation 'compile'"):
        case_text_argument(invalid_case)


def test_case_text_argument_rejects_non_text_payloads() -> None:
    module_case = replace(
        SYNTHETIC_MODULE_PATTERN_CASE,
        operation="module_call",
        helper="sub",
        source_args=[SYNTHETIC_CASE_PATTERN, r"<\g<word>>", object()],
        args=[SYNTHETIC_CASE_PATTERN, r"<\g<word>>", object()],
    )
    pattern_case = replace(
        SYNTHETIC_COMPILED_PATTERN_CASE,
        operation="pattern_call",
        helper="sub",
        source_args=[r"<\g<word>>", object()],
        args=[r"<\g<word>>", object()],
    )

    with pytest.raises(AssertionError):
        case_text_argument(module_case)

    with pytest.raises(AssertionError):
        case_text_argument(pattern_case)


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_MODULE_PATTERN_CASE, id="raw-module-str"),
        pytest.param(SYNTHETIC_MODULE_BYTES_SEARCH_CASE, id="raw-module-bytes"),
        pytest.param(
            SYNTHETIC_INCLUDE_PATTERN_MODULE_KEYWORD_CASE,
            id="raw-module-include-pattern-keyword-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
            id="compiled-module-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
            id="compiled-module-bytes",
        ),
    ),
)
def test_fixture_case_module_call_args_return_isolated_helper_arguments(
    case: FixtureCase,
) -> None:
    original_args = list(case.args)
    compiled_pattern = object()

    observed = case.module_call_args(
        compiled_pattern if case.use_compiled_pattern else None
    )

    assert observed is not case.args
    if case.use_compiled_pattern:
        assert observed[0] is compiled_pattern
        assert observed[1:] == original_args
    elif case.include_pattern_arg:
        assert observed[0] == case.pattern_payload()
        assert observed[1:] == original_args
    else:
        assert observed == original_args

    observed.append("mutated")
    assert case.args == original_args


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
            id="compiled-module-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
            id="compiled-module-bytes",
        ),
    ),
)
def test_fixture_case_module_call_args_require_compiled_pattern_argument(
    case: FixtureCase,
) -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"case {case.case_id!r} requires a compiled pattern helper argument"
        ),
    ):
        case.module_call_args()


def test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids() -> None:
    manifests = assert_published_manifest_helper_contract(
        published_fixture_manifests,
        expected_paths=DEFAULT_FIXTURE_PATHS,
    )
    assert_published_manifest_inventory_contract(
        manifests,
        child_records="cases",
        child_id="case_id",
        extra_manifest_unique_fields=("suite_id",),
    )


def test_default_fixture_inventory_serialized_case_payloads_are_json_safe_and_exercise_special_normalization_paths(
) -> None:
    manifests = published_fixture_manifests()
    cases = [case for manifest in manifests for case in manifest.cases]

    observed_payload_type_markers: Counter[str] = Counter()
    bytes_pattern_cases = 0
    nonempty_kwargs_cases = 0

    for case in cases:
        if case.pattern is not None:
            pattern_payload = case.pattern_payload()
            if case.text_model == "bytes":
                assert isinstance(pattern_payload, bytes)
                bytes_pattern_cases += 1
            else:
                assert isinstance(pattern_payload, str)

        serialized_args = case.serialized_args()
        serialized_kwargs = case.serialized_kwargs()

        json.dumps({"args": serialized_args, "kwargs": serialized_kwargs}, sort_keys=True)
        _assert_json_literal_safe(serialized_args)
        _assert_json_literal_safe(serialized_kwargs)
        observed_payload_type_markers.update(_payload_type_markers(serialized_args))
        observed_payload_type_markers.update(_payload_type_markers(serialized_kwargs))

        if serialized_kwargs:
            nonempty_kwargs_cases += 1

    assert bytes_pattern_cases > 0
    assert nonempty_kwargs_cases > 0
    assert observed_payload_type_markers["normalized-bytes"] > 0
    assert observed_payload_type_markers["callable"] > 0


def test_fixture_case_pattern_payload_supports_encoding_override_and_clear_errors(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_fixture_module(
        tmp_path,
        "pattern_payload_contract.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "pattern-payload-contract",
            "defaults": {
                "operation": "compile",
                "text_model": "bytes",
                "pattern_encoding": "latin-1",
            },
            "cases": [
                {
                    "id": "compile-pattern-utf8-bytes",
                    "pattern": "caf\\u00e9",
                    "pattern_encoding": "utf-8",
                },
                {
                    "id": "compile-pattern-invalid-text-model",
                    "pattern": "abc",
                    "text_model": "utf-16",
                },
                {
                    "id": "compile-pattern-missing-pattern",
                },
            ],
        }
        """,
    )

    cases = load_fixture_manifest(fixture_path).cases
    encoded_case, invalid_text_model_case, missing_pattern_case = cases

    assert encoded_case.pattern == "caf\u00e9"
    assert encoded_case.pattern_encoding == "utf-8"
    assert encoded_case.pattern_payload() == b"caf\xc3\xa9"

    with pytest.raises(ValueError, match=r"unsupported text model 'utf-16'"):
        invalid_text_model_case.pattern_payload()

    with pytest.raises(
        ValueError,
        match=r"case 'compile-pattern-missing-pattern' is missing a pattern payload",
    ):
        missing_pattern_case.pattern_payload()


def test_fixture_manifest_loads_use_compiled_pattern_for_module_call_rows(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_fixture_module(
        tmp_path,
        "compiled_module_call_contract.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "compiled-module-call-contract",
            "layer": "module_workflow",
            "defaults": {
                "operation": "module_call",
            },
            "cases": [
                {
                    "id": "raw-module-search",
                    "helper": "search",
                    "args": ["abc", "zzabczz"],
                },
                {
                    "id": "compiled-module-search",
                    "helper": "search",
                    "pattern": "abc",
                    "args": ["zzabczz"],
                    "use_compiled_pattern": True,
                },
            ],
        }
        """,
    )

    raw_case, compiled_case = load_fixture_manifest(fixture_path).cases

    assert raw_case.use_compiled_pattern is False
    assert raw_case.args == ["abc", "zzabczz"]
    assert compiled_case.use_compiled_pattern is True
    assert compiled_case.pattern == "abc"
    assert compiled_case.args == ["zzabczz"]


@pytest.mark.parametrize(
    ("filename", "source", "expected_suite_id", "expected_layer", "expected_operation"),
    (
        pytest.param(
            "parser_compile_default.py",
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "parser-compile-default",
                "cases": [
                    {
                        "id": "compile-case",
                        "pattern": "abc",
                    },
                ],
            }
            """,
            "parser.compile",
            "parser_acceptance_and_diagnostics",
            "compile",
            id="parser-compile-default",
        ),
        pytest.param(
            "module_workflow_default.py",
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "module-workflow-default",
                "layer": "module_workflow",
                "defaults": {
                    "operation": "module_call",
                },
                "cases": [
                    {
                        "id": "module-case",
                    },
                ],
            }
            """,
            "module-workflow-default",
            "module_workflow",
            "module_call",
            id="module-workflow-default",
        ),
        pytest.param(
            "parser_non_compile_default.py",
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "parser-non-compile-default",
                "defaults": {
                    "operation": "module_call",
                },
                "cases": [
                    {
                        "id": "parser-non-compile-case",
                    },
                ],
            }
            """,
            "parser-non-compile-default",
            "parser_acceptance_and_diagnostics",
            "module_call",
            id="parser-non-compile-default",
        ),
    ),
)
def test_fixture_manifest_defaults_suite_id_from_layer_and_operation(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
    expected_suite_id: str,
    expected_layer: str,
    expected_operation: str,
) -> None:
    fixture_path = _write_fixture_module(tmp_path, filename, source)

    manifest = load_fixture_manifest(fixture_path)
    cases = manifest.cases

    assert manifest.suite_id == expected_suite_id
    assert manifest.layer == expected_layer
    assert len(cases) == 1
    assert cases[0].suite_id == expected_suite_id
    assert cases[0].layer == expected_layer
    assert cases[0].operation == expected_operation


def test_fixture_manifest_loads_supported_scalar_defaults_and_case_overrides(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_fixture_module(
        tmp_path,
        "scalar_default_contract.py",
        """
        import re

        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "scalar-default-contract",
            "layer": "module_workflow",
            "defaults": {
                "family": "default-family",
                "operation": "module_call",
                "flags": re.IGNORECASE,
                "text_model": "bytes",
                "pattern_encoding": "utf-8",
                "use_compiled_pattern": True,
                "include_pattern_arg": False,
            },
            "cases": [
                {
                    "id": "defaulted-module-search",
                    "helper": "search",
                    "pattern": "caf\\u00e9",
                    "args": [b"zzcaf\\xc3\\xa9zz"],
                },
                {
                    "id": "overridden-module-search",
                    "helper": "search",
                    "family": "override-family",
                    "pattern": "abc",
                    "flags": re.MULTILINE,
                    "text_model": "str",
                    "pattern_encoding": "latin-1",
                    "use_compiled_pattern": False,
                    "include_pattern_arg": True,
                    "args": ["zzabczz"],
                },
            ],
        }
        """,
    )

    manifest = load_fixture_manifest(fixture_path)
    defaulted_case, overridden_case = manifest.cases
    compiled_pattern = object()

    assert manifest.defaults == {
        "family": "default-family",
        "operation": "module_call",
        "flags": re.IGNORECASE,
        "text_model": "bytes",
        "pattern_encoding": "utf-8",
        "use_compiled_pattern": True,
        "include_pattern_arg": False,
    }

    assert defaulted_case.family == "default-family"
    assert defaulted_case.operation == "module_call"
    assert defaulted_case.flags == int(re.IGNORECASE)
    assert defaulted_case.text_model == "bytes"
    assert defaulted_case.pattern_encoding == "utf-8"
    assert defaulted_case.use_compiled_pattern is True
    assert defaulted_case.include_pattern_arg is False
    assert defaulted_case.pattern_payload() == b"caf\xc3\xa9"
    assert defaulted_case.module_call_args(compiled_pattern) == [
        compiled_pattern,
        b"zzcaf\xc3\xa9zz",
    ]

    assert overridden_case.family == "override-family"
    assert overridden_case.operation == "module_call"
    assert overridden_case.flags == int(re.MULTILINE)
    assert overridden_case.text_model == "str"
    assert overridden_case.pattern_encoding == "latin-1"
    assert overridden_case.use_compiled_pattern is False
    assert overridden_case.include_pattern_arg is True
    assert overridden_case.pattern_payload() == "abc"
    assert overridden_case.module_call_args(compiled_pattern) == ["abc", "zzabczz"]


def test_fixture_manifest_loader_isolates_default_args_and_kwargs_per_case(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_fixture_module(
        tmp_path,
        "default_argument_isolation_contract.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "default-argument-isolation-contract",
            "layer": "module_workflow",
            "defaults": {
                "operation": "module_call",
                "text_model": "str",
                "args": ["payload", ["shared-arg"]],
                "kwargs": {
                    "window": [1, 4],
                    "metadata": {"label": "shared-kwarg"},
                },
            },
            "cases": [
                {
                    "id": "first-default-contract-case",
                    "helper": "search",
                    "pattern": "abc",
                    "include_pattern_arg": True,
                },
                {
                    "id": "second-default-contract-case",
                    "helper": "search",
                    "pattern": "def",
                    "include_pattern_arg": True,
                },
            ],
        }
        """,
    )

    manifest = load_fixture_manifest(fixture_path)
    first_case, second_case = manifest.cases
    expected_source_args = ["payload", ["shared-arg"]]
    expected_source_kwargs = {
        "window": [1, 4],
        "metadata": {"label": "shared-kwarg"},
    }

    assert manifest.defaults["args"] == expected_source_args
    assert manifest.defaults["kwargs"] == expected_source_kwargs

    assert first_case.source_args == expected_source_args
    assert second_case.source_args == expected_source_args
    assert first_case.args == expected_source_args
    assert second_case.args == expected_source_args
    assert first_case.source_kwargs == expected_source_kwargs
    assert second_case.source_kwargs == expected_source_kwargs
    assert first_case.kwargs == expected_source_kwargs
    assert second_case.kwargs == expected_source_kwargs

    assert first_case.source_args is not second_case.source_args
    assert first_case.source_args[1] is not second_case.source_args[1]
    assert first_case.args is not second_case.args
    assert first_case.args[1] is not second_case.args[1]
    assert first_case.source_kwargs is not second_case.source_kwargs
    assert first_case.source_kwargs["window"] is not second_case.source_kwargs["window"]
    assert first_case.kwargs is not second_case.kwargs
    assert first_case.kwargs["window"] is not second_case.kwargs["window"]

    first_case.source_args[1].append("source-args-mutation")
    first_case.source_kwargs["window"].append(7)
    first_case.source_kwargs["metadata"]["label"] = "source-kwargs-mutation"

    assert first_case.args == expected_source_args
    assert first_case.kwargs == expected_source_kwargs

    first_case.args[1].append("args-mutation")
    first_case.kwargs["window"].append(9)
    first_case.kwargs["metadata"]["label"] = "kwargs-mutation"

    assert second_case.source_args == expected_source_args
    assert second_case.args == expected_source_args
    assert second_case.source_kwargs == expected_source_kwargs
    assert second_case.kwargs == expected_source_kwargs
    assert manifest.defaults["args"] == expected_source_args
    assert manifest.defaults["kwargs"] == expected_source_kwargs


@pytest.mark.parametrize(
    ("filename", "source", "error_pattern"),
    (
        pytest.param(
            "non_python_suffix.json",
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "non-python-suffix",
                "cases": [],
            }
            """,
            r"fixture manifests must be Python modules",
            id="non-python-suffix",
        ),
        pytest.param(
            "unsupported_schema.py",
            """
            MANIFEST = {
                "schema_version": 99,
                "manifest_id": "unsupported-schema",
                "cases": [],
            }
            """,
            r"unsupported fixture schema version 99; expected 1",
            id="unsupported-schema",
        ),
        pytest.param(
            "non_dict_defaults.py",
            """
            MANIFEST = {
                "schema_version": 1,
                "manifest_id": "non-dict-defaults",
                "defaults": ["not-a-dict"],
                "cases": [],
            }
            """,
            r"fixture manifest defaults must be an object",
            id="non-dict-defaults",
        ),
    ),
)
def test_fixture_manifest_loader_rejects_invalid_module_shape_details(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
    error_pattern: str,
) -> None:
    fixture_path = _write_fixture_module(tmp_path, filename, source)

    with pytest.raises(ValueError, match=error_pattern):
        load_fixture_manifest(fixture_path)


@pytest.mark.parametrize(
    ("filename", "source", "error_pattern"),
    (
        pytest.param(
            "missing_manifest.py",
            "FIXTURE = {}",
            r"is missing a MANIFEST value",
            id="missing-manifest",
        ),
        pytest.param(
            "non_dict_manifest.py",
            "MANIFEST = ['not-a-dict']",
            r"must be a dict",
            id="non-dict-manifest",
        ),
    ),
)
def test_fixture_manifest_loader_rejects_missing_and_non_dict_manifest_values(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
    error_pattern: str,
) -> None:
    fixture_path = _write_fixture_module(tmp_path, filename, source)

    with pytest.raises(ValueError, match=error_pattern):
        load_fixture_manifest(fixture_path)


@pytest.mark.parametrize(
    ("first_module", "second_module", "error_pattern"),
    (
        pytest.param(
            (
                "duplicate_fixture_manifest_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-correctness-manifest-id",
                    "cases": [
                        {
                            "id": "compile-case-a",
                            "pattern": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_fixture_manifest_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-correctness-manifest-id",
                    "cases": [
                        {
                            "id": "compile-case-b",
                            "pattern": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate fixture manifest id .*duplicate-correctness-manifest-id",
            id="duplicate-manifest-id",
        ),
        pytest.param(
            (
                "duplicate_fixture_case_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "correctness-duplicate-case-a",
                    "cases": [
                        {
                            "id": "duplicate-correctness-case-id",
                            "pattern": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_fixture_case_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "correctness-duplicate-case-b",
                    "cases": [
                        {
                            "id": "duplicate-correctness-case-id",
                            "pattern": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate fixture case id .*duplicate-correctness-case-id",
            id="duplicate-case-id",
        ),
    ),
)
def test_fixture_manifest_loader_rejects_duplicate_ids(
    tmp_path: pathlib.Path,
    first_module: tuple[str, str],
    second_module: tuple[str, str],
    error_pattern: str,
) -> None:
    first_path = _write_fixture_module(tmp_path, *first_module)
    second_path = _write_fixture_module(tmp_path, *second_module)

    with pytest.raises(ValueError, match=error_pattern):
        load_fixture_manifests([first_path, second_path])


def test_load_fixture_manifests_preserves_requested_path_order(
    tmp_path: pathlib.Path,
) -> None:
    first_path = _write_fixture_module(
        tmp_path,
        "ordered_fixture_manifest_a.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "ordered-correctness-manifest-a",
            "cases": [
                {
                    "id": "ordered-correctness-case-a",
                    "pattern": "abc",
                },
            ],
        }
        """,
    )
    second_path = _write_fixture_module(
        tmp_path,
        "ordered_fixture_manifest_b.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "ordered-correctness-manifest-b",
            "cases": [
                {
                    "id": "ordered-correctness-case-b",
                    "pattern": "def",
                },
            ],
        }
        """,
    )

    manifests = load_fixture_manifests([second_path, first_path])

    assert [manifest.path for manifest in manifests] == [second_path, first_path]
    assert [manifest.manifest_id for manifest in manifests] == [
        "ordered-correctness-manifest-b",
        "ordered-correctness-manifest-a",
    ]
    assert [manifest.cases[0].case_id for manifest in manifests] == [
        "ordered-correctness-case-b",
        "ordered-correctness-case-a",
    ]


def test_published_fixture_manifests_cache_clear_reloads_current_default_fixture_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    first_path = _write_fixture_module(
        tmp_path,
        "cached_fixture_manifest_a.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "cached-correctness-manifest-a",
            "cases": [
                {
                    "id": "cached-correctness-case-a",
                    "pattern": "abc",
                },
            ],
        }
        """,
    )
    second_path = _write_fixture_module(
        tmp_path,
        "cached_fixture_manifest_b.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "cached-correctness-manifest-b",
            "cases": [
                {
                    "id": "cached-correctness-case-b",
                    "pattern": "def",
                },
            ],
        }
        """,
    )
    requested_paths = (second_path, first_path)
    loader_calls: list[tuple[pathlib.Path, ...]] = []
    real_load_fixture_manifests = correctness.load_fixture_manifests

    def _recording_loader(paths: tuple[pathlib.Path, ...]) -> list[FixtureManifest]:
        loader_calls.append(tuple(paths))
        return real_load_fixture_manifests(paths)

    monkeypatch.setattr(correctness, "DEFAULT_FIXTURE_PATHS", requested_paths)
    monkeypatch.setattr(correctness, "load_fixture_manifests", _recording_loader)
    assert_published_manifest_helper_reload_contract(
        published_fixture_manifests,
        clear_cache=correctness.published_fixture_manifests.cache_clear,
        expected_paths=requested_paths,
        expected_manifest_ids=(
            "cached-correctness-manifest-b",
            "cached-correctness-manifest-a",
        ),
        observed_load_calls=loader_calls,
    )


def test_direct_test_case_id_bucket_helper_accepts_exact_selected_frontier_coverage(
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "module": frozenset({"grouped-module-fullmatch-two-capture-gap-str"}),
            "pattern": frozenset({"grouped-pattern-fullmatch-two-capture-gap-str"}),
        },
        selected_case_ids=(
            "grouped-module-fullmatch-two-capture-gap-str",
            "grouped-pattern-fullmatch-two-capture-gap-str",
        ),
        coverage_label="fixture parity support contract buckets",
    )


def test_direct_test_case_id_bucket_helper_rejects_empty_selected_frontier() -> None:
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract buckets selected_case_ids must not be empty"
        ),
    ):
        assert_direct_test_case_id_buckets_cover_selected_frontier(
            {},
            selected_case_ids=(),
            coverage_label="fixture parity support contract buckets",
        )


def test_direct_test_case_id_bucket_helper_rejects_duplicate_selected_ids() -> None:
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract buckets selected_case_ids contain "
            "duplicate ids: ('grouped-module-fullmatch-two-capture-gap-str',)"
        ),
    ):
        assert_direct_test_case_id_buckets_cover_selected_frontier(
            {
                "module": frozenset({"grouped-module-fullmatch-two-capture-gap-str"}),
            },
            selected_case_ids=(
                "grouped-module-fullmatch-two-capture-gap-str",
                "grouped-module-fullmatch-two-capture-gap-str",
            ),
            coverage_label="fixture parity support contract buckets",
        )


def test_direct_test_case_id_bucket_helper_reports_missing_and_unexpected_ids_clearly(
) -> None:
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract buckets drifted; "
            "missing case ids: ('grouped-pattern-fullmatch-two-capture-gap-str',); "
            "unexpected case ids: ('unexpected-case-id',)"
        ),
    ):
        assert_direct_test_case_id_buckets_cover_selected_frontier(
            {
                "module": frozenset({"grouped-module-fullmatch-two-capture-gap-str"}),
                "unexpected": frozenset({"unexpected-case-id"}),
            },
            selected_case_ids=(
                "grouped-module-fullmatch-two-capture-gap-str",
                "grouped-pattern-fullmatch-two-capture-gap-str",
            ),
            coverage_label="fixture parity support contract buckets",
        )


def test_direct_test_case_id_bucket_helper_rejects_duplicate_ids_across_named_buckets(
) -> None:
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract buckets drifted; "
            "duplicate case ids: (('grouped-module-fullmatch-two-capture-gap-str', ('module', 'pattern')),)"
        ),
    ):
        assert_direct_test_case_id_buckets_cover_selected_frontier(
            {
                "module": frozenset({"grouped-module-fullmatch-two-capture-gap-str"}),
                "pattern": frozenset({"grouped-module-fullmatch-two-capture-gap-str"}),
            },
            selected_case_ids=("grouped-module-fullmatch-two-capture-gap-str",),
            coverage_label="fixture parity support contract buckets",
        )


def test_direct_test_case_id_bucket_helper_rejects_duplicate_ids_across_positional_buckets(
) -> None:
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract buckets drifted; "
            "duplicate case ids: (('grouped-pattern-fullmatch-two-capture-gap-str', ('bucket[0]', 'bucket[1]')),)"
        ),
    ):
        assert_direct_test_case_id_buckets_cover_selected_frontier(
            (
                frozenset({"grouped-pattern-fullmatch-two-capture-gap-str"}),
                frozenset({"grouped-pattern-fullmatch-two-capture-gap-str"}),
            ),
            selected_case_ids=("grouped-pattern-fullmatch-two-capture-gap-str",),
            coverage_label="fixture parity support contract buckets",
        )


@pytest.mark.parametrize(
    (
        "module_bucket_label",
        "pattern_bucket_label",
        "follow_on_bucket_labels",
        "expected_duplicate_labels",
    ),
    (
        pytest.param(
            "shared-compile",
            "shared-pattern-fullmatch",
            ("mixed-follow-on",),
            ("shared-compile",),
            id="module-collides-with-shared-compile",
        ),
        pytest.param(
            "shared-module-search",
            "shared-module-search",
            ("mixed-follow-on",),
            ("shared-module-search",),
            id="module-and-pattern-collide",
        ),
        pytest.param(
            "shared-module-search",
            "shared-pattern-fullmatch",
            ("shared-pattern-fullmatch",),
            ("shared-pattern-fullmatch",),
            id="follow-on-collides-with-pattern",
        ),
        pytest.param(
            "shared-module-search",
            "shared-pattern-fullmatch",
            ("duplicate-follow-on", "duplicate-follow-on"),
            ("duplicate-follow-on",),
            id="follow-on-collides-with-follow-on",
        ),
    ),
)
def test_direct_test_case_id_buckets_for_follow_on_bundles_rejects_duplicate_bucket_labels(
    tmp_path: pathlib.Path,
    module_bucket_label: str,
    pattern_bucket_label: str,
    follow_on_bucket_labels: tuple[str, ...],
    expected_duplicate_labels: tuple[str, ...],
) -> None:
    bundle = _load_bundle_loader_contract_mixed_bundle(tmp_path)

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "direct-test case-id buckets contain duplicate labels: "
            f"{expected_duplicate_labels}"
        ),
    ):
        fixture_parity_support.direct_test_case_id_buckets_for_follow_on_bundles(
            compile_cases=(),
            module_cases=(),
            pattern_cases=(),
            module_bucket_label=module_bucket_label,
            pattern_bucket_label=pattern_bucket_label,
            follow_on_buckets=(
                (bucket_label, bundle) for bucket_label in follow_on_bucket_labels
            ),
        )


@pytest.mark.parametrize(
    ("compiled_pattern", "case", "expected"),
    (
        pytest.param(
            re.compile("abc"),
            SimpleNamespace(helper="search", string="abcabc", bounds=(3, 6)),
            ("abc", (3, 6)),
            id="search-honors-pos-and-endpos",
        ),
        pytest.param(
            re.compile("abc"),
            SimpleNamespace(helper="match", string="xxabc", bounds=(0, 5)),
            None,
            id="match-does-not-search-forward",
        ),
        pytest.param(
            re.compile("abc"),
            SimpleNamespace(helper="fullmatch", string="abcx", bounds=(0, 4)),
            None,
            id="fullmatch-does-not-relax-to-prefix-match",
        ),
        pytest.param(
            re.compile(rb"abc"),
            SimpleNamespace(helper="search", string=b"zzabczzabc", bounds=(5, 10)),
            (b"abc", (7, 10)),
            id="bytes-search-honors-pos-and-endpos",
        ),
    ),
)
def test_invoke_bounded_pattern_case_preserves_helper_and_bound_semantics(
    compiled_pattern: re.Pattern[str] | re.Pattern[bytes],
    case: SimpleNamespace,
    expected: tuple[str | bytes, tuple[int, int]] | None,
) -> None:
    observed = invoke_bounded_pattern_case(compiled_pattern, case)

    if expected is None:
        assert observed is None
        return

    expected_group0, expected_span = expected
    assert observed is not None
    assert observed.group(0) == expected_group0
    assert observed.span() == expected_span


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_MODULE_PATTERN_CASE, id="module-str"),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
            id="compiled-module-str",
        ),
        pytest.param(
            SYNTHETIC_PATTERN_KEYWORD_SEARCH_CASE,
            id="pattern-keyword-search-str",
        ),
        pytest.param(SYNTHETIC_MODULE_BYTES_SEARCH_CASE, id="module-bytes"),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
            id="compiled-module-bytes",
        ),
        pytest.param(SYNTHETIC_FULLMATCH_PATTERN_CASE, id="pattern-str"),
        pytest.param(SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE, id="pattern-bytes"),
    ),
)
def test_workflow_result_with_cpython_parity_accepts_representative_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)


def test_workflow_result_with_cpython_parity_accepts_compiled_module_keyword_value_cases(
    regex_backend: tuple[str, object],
) -> None:
    backend_name, backend = regex_backend

    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        SYNTHETIC_COMPILED_MODULE_KEYWORD_SPLIT_CASE,
    )

    assert_value_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_COMPILE_CASE,
            id="compiled-module-compile-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_COMPILE_INT_ZERO_CASE,
            id="compiled-module-compile-int-zero-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_COMPILE_BOOL_FALSE_CASE,
            id="compiled-module-compile-bool-false-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_BYTES_COMPILE_CASE,
            id="compiled-module-compile-bytes",
        ),
    ),
)
def test_workflow_result_with_cpython_parity_accepts_compiled_module_compile_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )
    observed_compiled, expected_compiled = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )

    assert observed is observed_compiled
    assert expected is expected_compiled
    assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            replace(
                SYNTHETIC_MODULE_PATTERN_CASE,
                case_id="synthetic-module-pattern-str-no-match",
                source_args=[SYNTHETIC_CASE_PATTERN, "zzzzz"],
                args=[SYNTHETIC_CASE_PATTERN, "zzzzz"],
            ),
            id="module-str",
        ),
        pytest.param(
            replace(
                SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
                case_id="synthetic-module-compiled-pattern-str-no-match",
                source_args=["zzzzz"],
                args=["zzzzz"],
            ),
            id="compiled-module-str",
        ),
        pytest.param(
            replace(
                SYNTHETIC_MODULE_BYTES_SEARCH_CASE,
                case_id="synthetic-module-pattern-bytes-no-match",
                source_args=[b"abc", b"zzzzz"],
                args=[b"abc", b"zzzzz"],
            ),
            id="module-bytes",
        ),
        pytest.param(
            replace(
                SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
                case_id="synthetic-module-compiled-pattern-bytes-no-match",
                source_args=[b"zzzzz"],
                args=[b"zzzzz"],
            ),
            id="compiled-module-bytes",
        ),
        pytest.param(
            replace(
                SYNTHETIC_FULLMATCH_PATTERN_CASE,
                case_id="synthetic-pattern-fullmatch-str-no-match",
                source_args=["abcx"],
                args=["abcx"],
            ),
            id="pattern-str",
        ),
        pytest.param(
            replace(
                SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE,
                case_id="synthetic-pattern-fullmatch-bytes-no-match",
                source_args=[b"abcx"],
                args=[b"abcx"],
            ),
            id="pattern-bytes",
        ),
    ),
)
def test_workflow_result_with_cpython_parity_accepts_shared_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_MODULE_PATTERN_CASE, id="module-str"),
        pytest.param(SYNTHETIC_MODULE_BYTES_SEARCH_CASE, id="module-bytes"),
        pytest.param(
            SYNTHETIC_INCLUDE_PATTERN_MODULE_KEYWORD_CASE,
            id="module-include-pattern-keyword-str",
        ),
    ),
)
def test_workflow_result_with_cpython_parity_skips_compile_for_raw_module_calls(
    monkeypatch: pytest.MonkeyPatch,
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    def unexpected_compile(*args: object, **kwargs: object) -> tuple[object, object]:
        raise AssertionError("raw module helper should not compile through parity helper")

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        unexpected_compile,
    )

    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)


@pytest.mark.parametrize(
    ("case", "expected_pattern_payload"),
    (
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
            SYNTHETIC_CASE_PATTERN,
            id="compiled-module-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
            b"abc",
            id="compiled-module-bytes",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_KEYWORD_SPLIT_CASE,
            "abc",
            id="compiled-module-keyword-split-str",
        ),
    ),
)
def test_workflow_result_with_cpython_parity_routes_compiled_module_cases_through_module_call_args(
    monkeypatch: pytest.MonkeyPatch,
    case: FixtureCase,
    expected_pattern_payload: str | bytes,
) -> None:
    compile_calls: list[tuple[str, object, str | bytes, int]] = []
    observed_pattern = object()
    expected_pattern = object()

    def fake_compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
    ) -> tuple[object, object]:
        compile_calls.append((backend_name, backend, pattern, flags))
        return observed_pattern, expected_pattern

    class RecordingHelperTarget:
        def __init__(self, result: object) -> None:
            self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
            self._result = result

        def __getattr__(self, helper_name: str) -> Callable[..., object]:
            def invoke(*args: object, **kwargs: object) -> object:
                self.calls.append((helper_name, args, dict(kwargs)))
                return self._result

            return invoke

    fake_backend = RecordingHelperTarget("observed-result")
    fake_re = RecordingHelperTarget("expected-result")
    backend_name = "synthetic-backend"

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        fake_compile,
    )
    monkeypatch.setattr(fixture_parity_support, "re", fake_re)

    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        fake_backend,
        case,
    )

    assert compile_calls == [
        (backend_name, fake_backend, expected_pattern_payload, 0),
    ]
    assert fake_backend.calls == [
        (case.helper, tuple(case.module_call_args(observed_pattern)), dict(case.kwargs)),
    ]
    assert fake_re.calls == [
        (case.helper, tuple(case.module_call_args(expected_pattern)), dict(case.kwargs)),
    ]
    assert observed == "observed-result"
    assert expected == "expected-result"


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_COMPILE_CASE,
            id="compiled-module-compile-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_COMPILE_INT_ZERO_CASE,
            id="compiled-module-compile-int-zero-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_COMPILE_BOOL_FALSE_CASE,
            id="compiled-module-compile-bool-false-str",
        ),
        pytest.param(
            SYNTHETIC_COMPILED_MODULE_BYTES_COMPILE_CASE,
            id="compiled-module-compile-bytes",
        ),
    ),
)
def test_workflow_result_with_cpython_parity_routes_compiled_module_compile_cases_through_module_call_args(
    monkeypatch: pytest.MonkeyPatch,
    case: FixtureCase,
) -> None:
    compile_calls: list[tuple[str, object, str | bytes, int]] = []
    observed_pattern = object()
    expected_pattern = object()

    def fake_compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
    ) -> tuple[object, object]:
        compile_calls.append((backend_name, backend, pattern, flags))
        return observed_pattern, expected_pattern

    class RecordingCompileTarget:
        def __init__(self) -> None:
            self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

        def compile(self, *args: object, **kwargs: object) -> object:
            self.calls.append(("compile", args, dict(kwargs)))
            return args[0]

    fake_backend = RecordingCompileTarget()
    fake_re = RecordingCompileTarget()
    backend_name = "synthetic-backend"

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        fake_compile,
    )
    monkeypatch.setattr(fixture_parity_support, "re", fake_re)

    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        fake_backend,
        case,
    )

    assert compile_calls == [
        (backend_name, fake_backend, case_pattern(case), case.flags or 0),
    ]
    assert fake_backend.calls == [
        ("compile", tuple(case.module_call_args(observed_pattern)), dict(case.kwargs)),
    ]
    assert fake_re.calls == [
        ("compile", tuple(case.module_call_args(expected_pattern)), dict(case.kwargs)),
    ]
    assert observed is observed_pattern
    assert expected is expected_pattern


@pytest.mark.parametrize(
    ("case", "expected_pattern_payload"),
    (
        pytest.param(
            SYNTHETIC_FULLMATCH_PATTERN_CASE,
            SYNTHETIC_CASE_PATTERN,
            id="pattern-str",
        ),
        pytest.param(
            SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE,
            b"abc",
            id="pattern-bytes",
        ),
        pytest.param(
            SYNTHETIC_PATTERN_KEYWORD_SEARCH_CASE,
            "abc",
            id="pattern-keyword-search-str",
        ),
    ),
)
def test_workflow_result_with_cpython_parity_routes_pattern_calls_through_compiled_patterns(
    monkeypatch: pytest.MonkeyPatch,
    case: FixtureCase,
    expected_pattern_payload: str | bytes,
) -> None:
    compile_calls: list[tuple[str, object, str | bytes, int]] = []

    class RecordingPattern:
        def __init__(self, result: object) -> None:
            self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
            self._result = result

        def __getattr__(self, helper_name: str) -> Callable[..., object]:
            def invoke(*args: object, **kwargs: object) -> object:
                self.calls.append((helper_name, args, dict(kwargs)))
                return self._result

            return invoke

    observed_pattern = RecordingPattern("observed-result")
    expected_pattern = RecordingPattern("expected-result")
    fake_backend = object()
    backend_name = "synthetic-backend"

    def fake_compile(
        compile_backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
    ) -> tuple[RecordingPattern, RecordingPattern]:
        compile_calls.append((compile_backend_name, backend, pattern, flags))
        return observed_pattern, expected_pattern

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        fake_compile,
    )

    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        fake_backend,
        case,
    )

    assert compile_calls == [
        (backend_name, fake_backend, expected_pattern_payload, 0),
    ]
    assert observed_pattern.calls == [
        (case.helper, tuple(case.args), dict(case.kwargs)),
    ]
    assert expected_pattern.calls == [
        (case.helper, tuple(case.args), dict(case.kwargs)),
    ]
    assert observed == "observed-result"
    assert expected == "expected-result"


def test_workflow_result_with_cpython_parity_rejects_helperless_cases(
    regex_backend: tuple[str, object],
) -> None:
    backend_name, backend = regex_backend

    with pytest.raises(AssertionError):
        workflow_result_with_cpython_parity(
            backend_name,
            backend,
            replace(SYNTHETIC_MODULE_PATTERN_CASE, helper=None),
        )


@pytest.mark.parametrize(
    ("check_convenience_api", "check_group_access", "expected_helper_calls"),
    (
        pytest.param(
            True,
            False,
            ("match", "convenience"),
            id="convenience-only",
        ),
        pytest.param(
            False,
            True,
            ("match", "valid-group-access", "invalid-group-access"),
            id="group-access-only",
        ),
        pytest.param(
            True,
            True,
            (
                "match",
                "convenience",
                "valid-group-access",
                "invalid-group-access",
            ),
            id="convenience-and-group-access",
        ),
    ),
)
def test_optional_match_case_parity_runs_baseline_match_parity_before_optional_checks(
    monkeypatch: pytest.MonkeyPatch,
    check_convenience_api: bool,
    check_group_access: bool,
    expected_helper_calls: tuple[str, ...],
) -> None:
    helper_calls: list[tuple[str, dict[str, object]]] = []

    def record_call(name: str):
        def recorder(*args: object, **kwargs: object) -> None:
            helper_calls.append((name, dict(kwargs)))

        return recorder

    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_parity",
        record_call("match"),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        record_call("convenience"),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        record_call("valid-group-access"),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        record_call("invalid-group-access"),
    )
    observed_match = object()
    expected_match = object()

    class _RecordingBackend:
        def search(self, *args: object, **kwargs: object) -> object:
            return observed_match

    monkeypatch.setattr(
        fixture_parity_support,
        "re",
        SimpleNamespace(search=lambda *args, **kwargs: expected_match),
    )

    assert_fixture_case_optional_match_parity(
        ("rebar", _RecordingBackend()),
        SYNTHETIC_MODULE_PATTERN_CASE,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
        check_convenience_api=check_convenience_api,
        check_group_access=check_group_access,
    )

    assert tuple(name for name, _ in helper_calls) == expected_helper_calls
    assert helper_calls[0] == ("match", {"check_regs": True})
    assert all(kwargs == {} for _, kwargs in helper_calls[1:])


def test_optional_match_case_parity_returns_early_for_shared_no_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper_calls: list[str] = []

    def _unexpected_helper(*args: object, **kwargs: object) -> None:
        helper_calls.append("unexpected")

    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_parity",
        _unexpected_helper,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        _unexpected_helper,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        _unexpected_helper,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        _unexpected_helper,
    )
    no_match_case = replace(
        SYNTHETIC_MODULE_PATTERN_CASE,
        case_id="synthetic-module-pattern-str-no-match-early-return",
        source_args=[SYNTHETIC_CASE_PATTERN, "zzzzz"],
        args=[SYNTHETIC_CASE_PATTERN, "zzzzz"],
    )

    class _RecordingBackend:
        def search(
            self,
            *args: object,
            **kwargs: object,
        ) -> re.Match[str] | None:
            return None

    monkeypatch.setattr(
        fixture_parity_support,
        "re",
        SimpleNamespace(search=lambda *args, **kwargs: None),
    )

    assert_fixture_case_optional_match_parity(
        ("stub-backend", _RecordingBackend()),
        no_match_case,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )

    assert helper_calls == []


def test_fixture_case_optional_match_parity_helper_keeps_raw_module_calls_on_module_helper_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    expected_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def _unexpected_compile(*args: object, **kwargs: object) -> object:
        raise AssertionError("compile_with_cpython_parity should not run")

    class _RecordingBackend:
        def search(self, *args: object, **kwargs: object) -> re.Match[str] | None:
            observed_calls.append((args, dict(kwargs)))
            return re.search(*args, **kwargs)

    def _expected_search(*args: object, **kwargs: object) -> re.Match[str] | None:
        expected_calls.append((args, dict(kwargs)))
        return re.search(*args, **kwargs)

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        _unexpected_compile,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "re",
        SimpleNamespace(search=_expected_search),
    )

    assert_fixture_case_optional_match_parity(
        ("stub-backend", _RecordingBackend()),
        SYNTHETIC_MODULE_PATTERN_CASE,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
    )

    expected_args = tuple(SYNTHETIC_MODULE_PATTERN_CASE.module_call_args())
    assert observed_calls == [(expected_args, {})]
    assert expected_calls == [(expected_args, {})]


def test_fixture_case_optional_match_parity_helper_routes_compiled_module_calls_through_compiled_pattern_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compile_calls: list[tuple[object, ...]] = []
    observed_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    expected_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    observed_pattern = object()
    expected_pattern = re.compile(SYNTHETIC_CASE_PATTERN)

    def _compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
        *,
        check_cache_identity: bool = True,
    ) -> tuple[object, re.Pattern[str]]:
        compile_calls.append(
            (backend_name, backend, pattern, flags, check_cache_identity)
        )
        return observed_pattern, expected_pattern

    class _RecordingBackend:
        def search(self, *args: object, **kwargs: object) -> re.Match[str] | None:
            observed_calls.append((args, dict(kwargs)))
            assert args[0] is observed_pattern
            return re.search(SYNTHETIC_CASE_PATTERN, args[1], **kwargs)

    def _expected_search(*args: object, **kwargs: object) -> re.Match[str] | None:
        expected_calls.append((args, dict(kwargs)))
        return re.search(*args, **kwargs)

    monkeypatch.setattr(fixture_parity_support, "compile_with_cpython_parity", _compile)
    monkeypatch.setattr(
        fixture_parity_support,
        "re",
        SimpleNamespace(search=_expected_search),
    )

    backend = _RecordingBackend()
    assert_fixture_case_optional_match_parity(
        ("stub-backend", backend),
        SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
    )

    assert compile_calls == [
        ("stub-backend", backend, SYNTHETIC_CASE_PATTERN, 0, True)
    ]
    assert observed_calls == [
        (
            tuple(
                SYNTHETIC_COMPILED_MODULE_PATTERN_CASE.module_call_args(
                    observed_pattern
                )
            ),
            {},
        )
    ]
    assert expected_calls == [
        (
            tuple(
                SYNTHETIC_COMPILED_MODULE_PATTERN_CASE.module_call_args(
                    expected_pattern
                )
            ),
            {},
        )
    ]


def test_fixture_case_optional_match_parity_helper_routes_pattern_calls_through_compiled_patterns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compile_calls: list[tuple[object, ...]] = []
    observed_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    expected_pattern = re.compile(SYNTHETIC_CASE_PATTERN)

    def _observed_fullmatch(
        *args: object,
        **kwargs: object,
    ) -> re.Match[str] | None:
        observed_calls.append((args, dict(kwargs)))
        return re.fullmatch(SYNTHETIC_CASE_PATTERN, *args, **kwargs)

    def _compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
        *,
        check_cache_identity: bool = True,
    ) -> tuple[object, re.Pattern[str]]:
        compile_calls.append(
            (backend_name, backend, pattern, flags, check_cache_identity)
        )
        return SimpleNamespace(fullmatch=_observed_fullmatch), expected_pattern

    monkeypatch.setattr(fixture_parity_support, "compile_with_cpython_parity", _compile)

    backend = object()
    assert_fixture_case_optional_match_parity(
        ("stub-backend", backend),
        SYNTHETIC_FULLMATCH_PATTERN_CASE,
        expected_helper="fullmatch",
        compile_pattern=True,
        check_regs=True,
    )

    assert compile_calls == [
        (
            "stub-backend",
            backend,
            case_pattern(SYNTHETIC_FULLMATCH_PATTERN_CASE),
            0,
            True,
        )
    ]
    assert observed_calls == [(tuple(SYNTHETIC_FULLMATCH_PATTERN_CASE.args), {})]


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_MODULE_PATTERN_CASE, id="str-match"),
        pytest.param(SYNTHETIC_MODULE_BYTES_SEARCH_CASE, id="bytes-match"),
    ),
)
def test_fixture_case_optional_match_parity_helper_accepts_representative_search_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_fixture_case_optional_match_parity(
        regex_backend,
        case,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_COMPILED_MODULE_PATTERN_CASE, id="str-match"),
        pytest.param(SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE, id="bytes-match"),
    ),
)
def test_fixture_case_optional_match_parity_helper_accepts_compiled_search_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_fixture_case_optional_match_parity(
        regex_backend,
        case,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            replace(
                SYNTHETIC_MODULE_PATTERN_CASE,
                case_id="synthetic-module-pattern-str-no-match",
                source_args=[SYNTHETIC_CASE_PATTERN, "zzzzz"],
                args=[SYNTHETIC_CASE_PATTERN, "zzzzz"],
            ),
            id="str-no-match",
        ),
        pytest.param(
            replace(
                SYNTHETIC_MODULE_BYTES_SEARCH_CASE,
                case_id="synthetic-module-pattern-bytes-no-match",
                source_args=[b"abc", b"zzzzz"],
                args=[b"abc", b"zzzzz"],
            ),
            id="bytes-no-match",
        ),
    ),
)
def test_fixture_case_optional_match_parity_helper_accepts_search_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_fixture_case_optional_match_parity(
        regex_backend,
        case,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            replace(
                SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
                case_id="synthetic-module-compiled-pattern-str-no-match",
                source_args=["zzzzz"],
                args=["zzzzz"],
            ),
            id="str-no-match",
        ),
        pytest.param(
            replace(
                SYNTHETIC_COMPILED_MODULE_BYTES_SEARCH_CASE,
                case_id="synthetic-module-compiled-pattern-bytes-no-match",
                source_args=[b"zzzzz"],
                args=[b"zzzzz"],
            ),
            id="bytes-no-match",
        ),
    ),
)
def test_fixture_case_optional_match_parity_helper_accepts_compiled_search_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_fixture_case_optional_match_parity(
        regex_backend,
        case,
        expected_helper="search",
        compile_pattern=False,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


def test_fixture_case_optional_match_parity_helper_rejects_non_search_cases(
    regex_backend: tuple[str, object],
) -> None:
    with pytest.raises(AssertionError):
        assert_fixture_case_optional_match_parity(
            regex_backend,
            replace(SYNTHETIC_MODULE_PATTERN_CASE, helper="match"),
            expected_helper="search",
            compile_pattern=False,
        )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_FULLMATCH_PATTERN_CASE, id="str-match"),
        pytest.param(SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE, id="bytes-match"),
    ),
)
def test_fixture_case_optional_match_parity_helper_accepts_fullmatch_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_fixture_case_optional_match_parity(
        regex_backend,
        case,
        expected_helper="fullmatch",
        compile_pattern=True,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            replace(
                SYNTHETIC_FULLMATCH_PATTERN_CASE,
                case_id="synthetic-pattern-fullmatch-str-no-match",
                source_args=["abcx"],
                args=["abcx"],
            ),
            id="str-no-match",
        ),
        pytest.param(
            replace(
                SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE,
                case_id="synthetic-pattern-fullmatch-bytes-no-match",
                source_args=[b"abcx"],
                args=[b"abcx"],
            ),
            id="bytes-no-match",
        ),
    ),
)
def test_fixture_case_optional_match_parity_helper_accepts_fullmatch_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_fixture_case_optional_match_parity(
        regex_backend,
        case,
        expected_helper="fullmatch",
        compile_pattern=True,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


def test_fixture_case_optional_match_parity_helper_rejects_non_fullmatch_cases(
    regex_backend: tuple[str, object],
) -> None:
    with pytest.raises(AssertionError):
        assert_fixture_case_optional_match_parity(
            regex_backend,
            replace(SYNTHETIC_FULLMATCH_PATTERN_CASE, helper="search"),
            expected_helper="fullmatch",
            compile_pattern=True,
        )


def test_bounded_pattern_case_match_parity_compiles_then_dispatches_observed_and_expected_patterns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compile_calls: list[tuple[object, ...]] = []
    dispatched_patterns: list[tuple[object, object]] = []
    parity_calls: list[tuple[object, ...]] = []
    observed_pattern = object()
    expected_pattern = object()
    observed_match = object()
    expected_match = object()
    case = SimpleNamespace(
        pattern="abc",
        helper="search",
        string="zzabczz",
        bounds=(0, 7),
    )

    def _compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
        *,
        check_cache_identity: bool = True,
    ) -> tuple[object, object]:
        compile_calls.append(
            (backend_name, backend, pattern, flags, check_cache_identity)
        )
        return observed_pattern, expected_pattern

    def _invoke(compiled_pattern: object, routed_case: object) -> object:
        dispatched_patterns.append((compiled_pattern, routed_case))
        if compiled_pattern is observed_pattern:
            return observed_match
        assert compiled_pattern is expected_pattern
        return expected_match

    monkeypatch.setattr(fixture_parity_support, "compile_with_cpython_parity", _compile)
    monkeypatch.setattr(
        fixture_parity_support,
        "invoke_bounded_pattern_case",
        _invoke,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        lambda *args, **kwargs: parity_calls.append(args),
    )

    backend = object()
    assert_bounded_pattern_case_match_parity(
        ("stub-backend", backend),
        case,
    )
    assert compile_calls == [("stub-backend", backend, "abc", 0, True)]
    assert dispatched_patterns == [
        (observed_pattern, case),
        (expected_pattern, case),
    ]
    assert parity_calls == [("stub-backend", observed_match, expected_match)]


def test_bounded_pattern_case_match_parity_skips_follow_on_checks_for_expected_no_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compile_calls: list[tuple[object, ...]] = []
    dispatched_patterns: list[tuple[object, object]] = []
    helper_calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
    observed_pattern = object()
    expected_pattern = object()
    case = SimpleNamespace(
        pattern="abc",
        helper="fullmatch",
        string="abcx",
        bounds=(0, 4),
    )

    def _compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
        *,
        check_cache_identity: bool = True,
    ) -> tuple[object, object]:
        compile_calls.append(
            (backend_name, backend, pattern, flags, check_cache_identity)
        )
        return observed_pattern, expected_pattern

    def _invoke(compiled_pattern: object, routed_case: object) -> None:
        dispatched_patterns.append((compiled_pattern, routed_case))
        return None

    def _record_call(name: str):
        def recorder(*args: object, **kwargs: object) -> None:
            helper_calls.append((name, args, dict(kwargs)))

        return recorder

    monkeypatch.setattr(fixture_parity_support, "compile_with_cpython_parity", _compile)
    monkeypatch.setattr(
        fixture_parity_support,
        "invoke_bounded_pattern_case",
        _invoke,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        _record_call("match-result"),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        _record_call("convenience"),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        _record_call("valid-group-access"),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        _record_call("invalid-group-access"),
    )

    backend = object()
    assert_bounded_pattern_case_match_parity(
        ("stub-backend", backend),
        case,
        expect_match=False,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )

    assert compile_calls == [("stub-backend", backend, "abc", 0, True)]
    assert dispatched_patterns == [
        (observed_pattern, case),
        (expected_pattern, case),
    ]
    assert helper_calls == [
        ("match-result", ("stub-backend", None, None), {"check_regs": True})
    ]


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            SimpleNamespace(
                pattern=SYNTHETIC_CASE_PATTERN,
                helper="search",
                string="zzabczz",
                bounds=(0, 7),
            ),
            id="str-search-match",
        ),
        pytest.param(
            SimpleNamespace(
                pattern=BYTES_LITERAL_PATTERN,
                helper="search",
                string=b"zzabczz",
                bounds=(0, 7),
            ),
            id="bytes-search-match",
        ),
    ),
)
def test_bounded_pattern_case_match_parity_helper_accepts_representative_cases(
    regex_backend: tuple[str, object],
    case: SimpleNamespace,
) -> None:
    assert_bounded_pattern_case_match_parity(
        regex_backend,
        case,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(
            SimpleNamespace(
                pattern=SYNTHETIC_CASE_PATTERN,
                helper="fullmatch",
                string="abcx",
                bounds=(0, 4),
            ),
            id="str-fullmatch-no-match",
        ),
        pytest.param(
            SimpleNamespace(
                pattern=BYTES_LITERAL_PATTERN,
                helper="search",
                string=b"zzabczz",
                bounds=(0, 2),
            ),
            id="bytes-search-no-match",
        ),
    ),
)
def test_bounded_pattern_case_match_parity_helper_accepts_representative_no_match_cases(
    regex_backend: tuple[str, object],
    case: SimpleNamespace,
) -> None:
    assert_bounded_pattern_case_match_parity(
        regex_backend,
        case,
        expect_match=False,
        check_regs=True,
    )


def test_whole_manifest_bundle_contract_supports_full_manifest_counts_without_case_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    str_bundle, mixed_bundle = tuple(
        build_selected_fixture_bundle(path) for path in (str_path, mixed_path)
    )

    assert tuple(bundle.manifest.path.name for bundle in (str_bundle, mixed_bundle)) == (
        BUNDLE_LOADER_CONTRACT_STR_FILENAME,
        BUNDLE_LOADER_CONTRACT_MIXED_FILENAME,
    )
    assert_fixture_bundle_contract(
        str_bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
    )
    assert mixed_bundle.expected_case_ids is None
    assert_fixture_bundle_contract(
        mixed_bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=mixed_path,
    )


def test_selected_fixture_bundle_contract_supports_expected_case_ids_and_fixture_path_validation(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    selected_case_ids = (
        "bundle-loader-contract-compile-str",
        "bundle-loader-contract-module-search-str",
        "bundle-loader-contract-pattern-search-str",
    )
    bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=selected_case_ids,
        pattern_extractor=str_case_pattern,
    )

    assert bundle.manifest.path == str_path
    assert bundle.expected_case_ids == frozenset(selected_case_ids)
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
        expected_ordered_case_ids=selected_case_ids,
    )


def test_selected_fixture_bundle_preserves_explicit_expected_case_id_metadata(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    selected_case_ids = (
        "bundle-loader-contract-pattern-search-str",
        "bundle-loader-contract-compile-str",
    )
    explicit_expected_case_ids = frozenset(selected_case_ids)

    bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=selected_case_ids,
        pattern_extractor=str_case_pattern,
        expected_case_ids=explicit_expected_case_ids,
    )

    assert bundle.expected_case_ids is explicit_expected_case_ids
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
        expected_ordered_case_ids=selected_case_ids,
    )


def test_selected_fixture_bundle_preserves_explicit_expected_text_model_metadata(
    tmp_path: pathlib.Path,
) -> None:
    _, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    selected_case_ids = (
        "bundle-loader-contract-mixed-pattern-fullmatch-bytes",
        "bundle-loader-contract-mixed-module-search-str",
    )
    explicit_expected_text_models = frozenset({"bytes", "str"})

    bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=selected_case_ids,
        pattern_extractor=case_pattern,
        expected_text_models=explicit_expected_text_models,
    )

    assert bundle.expected_text_models is explicit_expected_text_models
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=mixed_path,
        expected_ordered_case_ids=selected_case_ids,
    )


def test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(
    tmp_path: pathlib.Path,
) -> None:
    field_names = {field.name for field in fields(FixtureBundle)}
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = _load_full_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )

    assert "expected_manifest_id" not in field_names
    assert bundle.expected_manifest_id == BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID
    assert bundle.expected_manifest_id == bundle.manifest.manifest_id


def test_full_manifest_bundle_builds_contracts_in_input_order(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles = tuple(build_selected_fixture_bundle(path) for path in (mixed_path, str_path))
    mixed_bundle, str_bundle = bundles

    assert tuple(bundle.expected_manifest_id for bundle in bundles) == (
        BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
        BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
    )
    assert mixed_bundle.expected_case_ids is None
    assert mixed_bundle.expected_patterns == frozenset(
        {r"a(bc|de){1,}d", rb"a(bc|de){1,}d"}
    )
    assert mixed_bundle.expected_operation_helper_counts == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 1,
            ("pattern_call", "fullmatch"): 1,
        }
    )
    assert mixed_bundle.expected_text_models == frozenset({"bytes", "str"})
    assert_fixture_bundle_contract(
        mixed_bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=mixed_path,
    )

    assert str_bundle.expected_case_ids is None
    assert str_bundle.expected_patterns == frozenset({r"(?P<word>ab)(?P=word)"})
    assert str_bundle.expected_operation_helper_counts == Counter(
        {
            ("compile", None): 1,
            ("module_call", "search"): 1,
            ("pattern_call", "search"): 1,
        }
    )
    assert str_bundle.expected_text_models == frozenset({"str"})
    assert_fixture_bundle_contract(
        str_bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
    )


def test_full_manifest_bundle_custom_pattern_extractor_only_changes_expected_patterns(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)

    default_bundles = tuple(
        build_selected_fixture_bundle(path) for path in (mixed_path, str_path)
    )

    def _case_id_pattern(case: FixtureCase) -> str:
        return case.case_id

    custom_bundles = tuple(
        build_selected_fixture_bundle(path, pattern_extractor=_case_id_pattern)
        for path in (mixed_path, str_path)
    )

    assert tuple(bundle.expected_manifest_id for bundle in custom_bundles) == tuple(
        bundle.expected_manifest_id for bundle in default_bundles
    )

    for default_bundle, custom_bundle, expected_path in zip(
        default_bundles,
        custom_bundles,
        (mixed_path, str_path),
        strict=True,
    ):
        assert (
            custom_bundle.manifest.path
            == default_bundle.manifest.path
            == expected_path
        )
        assert custom_bundle.manifest.manifest_id == default_bundle.manifest.manifest_id
        assert custom_bundle.cases == default_bundle.cases
        assert custom_bundle.expected_operation_helper_counts == (
            default_bundle.expected_operation_helper_counts
        )
        assert custom_bundle.expected_case_ids == default_bundle.expected_case_ids
        assert custom_bundle.expected_text_models == default_bundle.expected_text_models
        assert custom_bundle.expected_patterns == frozenset(
            case.case_id for case in custom_bundle.cases
        )
        assert_fixture_bundle_contract(
            custom_bundle,
            pattern_extractor=_case_id_pattern,
            expected_fixture_path=expected_path,
        )

    assert tuple(bundle.expected_patterns for bundle in custom_bundles) != tuple(
        bundle.expected_patterns for bundle in default_bundles
    )


def test_published_fixture_bundles_by_manifest_id_returns_requested_bundles(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles = tuple(
        build_selected_fixture_bundle(path) for path in (str_path, mixed_path)
    )

    bundles_by_manifest_id = fixture_parity_support.published_fixture_bundles_by_manifest_id(
        bundles
    )

    assert tuple(bundles_by_manifest_id) == (
        BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
        BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
    )
    assert bundles_by_manifest_id[BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID] is bundles[0]
    assert bundles_by_manifest_id[BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID] is bundles[1]
    assert fixture_parity_support.requested_published_fixture_bundles(
        bundles_by_manifest_id,
        (
            BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
            BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
        ),
    ) == (bundles[1], bundles[0])


def test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = build_selected_fixture_bundle(str_path)
    duplicate_bundle = replace(
        bundle,
        manifest=replace(
            bundle.manifest,
            path=bundle.manifest.path.with_name(
                f"duplicate_{bundle.manifest.path.name}"
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundles contain duplicate manifest_id "
            f"'{BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID}'"
        ),
    ):
        fixture_parity_support.published_fixture_bundles_by_manifest_id(
            (bundle, duplicate_bundle)
        )


def test_requested_published_fixture_bundles_rejects_missing_manifest_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles_by_manifest_id = fixture_parity_support.published_fixture_bundles_by_manifest_id(
        (build_selected_fixture_bundle(str_path),)
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundle mapping is missing manifest ids: "
            f"('{BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID}',)"
        ),
    ):
        fixture_parity_support.requested_published_fixture_bundles(
            bundles_by_manifest_id,
            (BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,),
        )


def test_load_published_fixture_bundles_preserves_selected_path_order(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    selector_paths = {
        "second-selector": (mixed_path,),
        "first-selector": (str_path,),
    }

    monkeypatch.setattr(
        fixture_parity_support,
        "select_correctness_fixture_paths",
        lambda selector: selector_paths[selector],
    )

    bundles, bundles_by_manifest_id = fixture_parity_support.load_published_fixture_bundles(
        ("second-selector", "first-selector"),
        pattern_extractor=case_pattern,
    )

    assert tuple(bundle.manifest.path.name for bundle in bundles) == (
        BUNDLE_LOADER_CONTRACT_MIXED_FILENAME,
        BUNDLE_LOADER_CONTRACT_STR_FILENAME,
    )
    assert tuple(bundle.expected_manifest_id for bundle in bundles) == (
        BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
        BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
    )
    assert tuple(bundles_by_manifest_id) == (
        BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
        BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
    )
    assert bundles_by_manifest_id[BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID] is bundles[0]
    assert bundles_by_manifest_id[BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID] is bundles[1]


def test_load_published_fixture_bundles_treats_single_selector_string_as_atomic(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    seen_selectors: list[str] = []

    def _select_paths(selector: str) -> tuple[pathlib.Path, ...]:
        seen_selectors.append(selector)
        return (str_path,) if selector == "single-selector" else ()

    monkeypatch.setattr(
        fixture_parity_support,
        "select_correctness_fixture_paths",
        _select_paths,
    )

    bundles, bundles_by_manifest_id = fixture_parity_support.load_published_fixture_bundles(
        "single-selector",
        pattern_extractor=case_pattern,
    )

    assert seen_selectors == ["single-selector"]
    assert tuple(bundle.manifest.path for bundle in bundles) == (str_path,)
    assert tuple(bundles_by_manifest_id) == (BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,)
    assert bundles_by_manifest_id[BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID] is bundles[0]


def test_load_single_published_fixture_bundle_returns_expected_manifest_contract(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)

    monkeypatch.setattr(
        fixture_parity_support,
        "select_correctness_fixture_paths",
        lambda selector: (str_path,) if selector == "single-selector" else (),
    )

    bundle = load_single_published_fixture_bundle("single-selector")

    assert bundle.manifest.path == str_path
    assert bundle.manifest.path.name == BUNDLE_LOADER_CONTRACT_STR_FILENAME
    assert bundle.expected_manifest_id == BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID


def test_load_single_published_fixture_bundle_rejects_zero_manifest_selector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fixture_parity_support,
        "select_correctness_fixture_paths",
        lambda selector: (),
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "correctness fixture selector 'missing-selector' resolved to 0 "
            "published fixture paths; expected exactly 1"
        ),
    ):
        load_single_published_fixture_bundle("missing-selector")


def test_load_single_published_fixture_bundle_rejects_multi_manifest_selector(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)

    monkeypatch.setattr(
        fixture_parity_support,
        "select_correctness_fixture_paths",
        lambda selector: (str_path, mixed_path) if selector == "multi-selector" else (),
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "correctness fixture selector 'multi-selector' resolved to 2 "
            "published fixture paths; expected exactly 1"
        ),
    ):
        load_single_published_fixture_bundle("multi-selector")


def test_load_published_fixture_bundles_rejects_duplicate_manifest_ids(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    selector_paths = {
        "first-selector": (str_path,),
        "duplicate-selector": (str_path,),
    }

    monkeypatch.setattr(
        fixture_parity_support,
        "select_correctness_fixture_paths",
        lambda selector: selector_paths[selector],
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundles contain duplicate manifest_id "
            f"'{BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID}'"
        ),
    ):
        fixture_parity_support.load_published_fixture_bundles(
            ("first-selector", "duplicate-selector"),
            pattern_extractor=case_pattern,
        )


def test_grouped_quantified_bytes_surface_spec_preserves_follow_on_id_and_bundle_identity(
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_workflows.py",
        pattern_extractor=case_pattern,
    )
    cases = (
        SupplementalCase(
            id="quantified-alternation-numbered-bytes",
            pattern=rb"a(b|c){1,2}d",
            search_matches=(b"zzacdz",),
            fullmatch_matches=(b"abcd",),
        ),
        SupplementalCase(
            id="quantified-alternation-named-bytes",
            pattern=rb"a(?P<word>b|c){1,2}d",
            search_matches=(b"zzacbdzz",),
            fullmatch_matches=(b"abd",),
        ),
    )
    surface = fixture_parity_support.GroupedQuantifiedBytesSurfaceSpec(
        bundle=bundle,
        cases=cases,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
        expected_module_search_texts_by_pattern={
            cases[0].pattern: frozenset(cases[0].search_matches),
            cases[1].pattern: frozenset(cases[1].search_matches),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            cases[0].pattern: frozenset(cases[0].fullmatch_matches),
            cases[1].pattern: frozenset(cases[1].fullmatch_matches),
        },
        follow_on_id="bounded",
    )

    assert surface.bundle is bundle
    assert surface.bundle.expected_manifest_id == "quantified-alternation-workflows"
    assert tuple(case.id for case in surface.cases) == (
        "quantified-alternation-numbered-bytes",
        "quantified-alternation-named-bytes",
    )
    assert surface.follow_on_id == "bounded"


def test_grouped_quantified_bytes_surface_spec_preserves_branch_local_counts_and_text_maps(
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT
        / "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
        pattern_extractor=case_pattern,
    )
    cases = (
        SupplementalCase(
            id="quantified-nested-group-alternation-branch-local-numbered-bytes",
            pattern=rb"a((b|c)+)\2d",
            search_matches=(b"zzabbdzz",),
            fullmatch_matches=(b"accd", b"abbbd"),
            fullmatch_misses=(b"abcd",),
        ),
        SupplementalCase(
            id="quantified-nested-group-alternation-branch-local-named-bytes",
            pattern=rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
            search_matches=(b"zzaccdzz",),
            fullmatch_matches=(b"abbd", b"abccd"),
            fullmatch_misses=(b"acbd",),
        ),
    )
    surface = fixture_parity_support.GroupedQuantifiedBytesSurfaceSpec(
        bundle=bundle,
        cases=cases,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            cases[0].pattern: frozenset(cases[0].search_matches),
            cases[1].pattern: frozenset(cases[1].search_matches),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            cases[0].pattern: frozenset(
                (*cases[0].fullmatch_matches, *cases[0].fullmatch_misses)
            ),
            cases[1].pattern: frozenset(
                (*cases[1].fullmatch_matches, *cases[1].fullmatch_misses)
            ),
        },
    )

    assert surface.bundle.expected_manifest_id == (
        "quantified-nested-group-alternation-branch-local-backreference-workflows"
    )
    assert surface.expected_operation_helper_counts == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 2,
            ("pattern_call", "fullmatch"): 6,
        }
    )
    assert surface.expected_module_search_texts_by_pattern == {
        rb"a((b|c)+)\2d": frozenset({b"zzabbdzz"}),
        rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d": frozenset({b"zzaccdzz"}),
    }
    assert surface.expected_pattern_fullmatch_texts_by_pattern == {
        rb"a((b|c)+)\2d": frozenset({b"accd", b"abbbd", b"abcd"}),
        rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d": frozenset(
            {b"abbd", b"abccd", b"acbd"}
        ),
    }


def test_grouped_quantified_bytes_surface_spec_preserves_supplemental_case_unsupported_backend_metadata(
) -> None:
    case = SupplementalCase(
        id="direct-bytes-case",
        pattern=rb"a((b|c)\2){1,2}d",
        search_matches=(b"zzabbdzz",),
        unsupported_backends=("rebar",),
        unsupported_backend_reason="known gap",
    )

    assert case.id == "direct-bytes-case"
    assert case.pattern == rb"a((b|c)\2){1,2}d"
    assert case.search_matches == (b"zzabbdzz",)
    assert case.unsupported_backends == ("rebar",)
    assert case.unsupported_backend_reason == "known gap"


def test_grouped_quantified_bytes_surface_spec_preserves_supported_direct_follow_on_surface_contract(
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT / "open_ended_quantified_group_alternation_workflows.py",
        pattern_extractor=case_pattern,
    )
    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (bundle,),
            (bundle,),
        )
    )
    surface = fixture_parity_support.GroupedQuantifiedBytesSurfaceSpec(
        bundle=bundle,
        cases=fixture_parity_support.OPEN_ENDED_ALTERNATION_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_module_search_texts_by_pattern={
            rb"a(bc|de){1,}d": frozenset({b"zzabcdzz", b"zzadedzz"}),
            rb"a(?P<word>bc|de){1,}d": frozenset({b"zzabcdzz", b"zzadedzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            rb"a(bc|de){1,}d": frozenset(
                {b"abcbcd", b"abcded", b"abcbcded", b"ad", b"abed"}
            ),
            rb"a(?P<word>bc|de){1,}d": frozenset(
                {b"abcded", b"abcbcded", b"adededed", b"ad", b"abed"}
            ),
        },
        follow_on_id="open-ended-alternation",
    )

    bundle_str_cases, bundle_bytes_cases = (
        fixture_parity_support.assert_grouped_quantified_direct_bytes_surface_spec(
            surface,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )
    )

    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 16
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 4,
            ("pattern_call", "fullmatch"): 10,
        }
    )


def test_grouped_quantified_bytes_surface_spec_preserves_branch_local_unsupported_backend_expectations(
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT
        / "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
        pattern_extractor=case_pattern,
    )
    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (bundle,),
            (bundle,),
        )
    )
    cases = (
        SupplementalCase(
            id="quantified-nested-group-alternation-branch-local-numbered-bytes",
            pattern=rb"a((b|c)+)\2d",
            search_matches=(b"zzabbdzz",),
            fullmatch_matches=(b"accd", b"abbbd"),
            fullmatch_misses=(b"abcd",),
            unsupported_backends=("rebar",),
            unsupported_backend_reason="known gap",
        ),
        SupplementalCase(
            id="quantified-nested-group-alternation-branch-local-named-bytes",
            pattern=rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
            search_matches=(b"zzaccdzz",),
            fullmatch_matches=(b"abbd", b"abccd"),
            fullmatch_misses=(b"acbd",),
            unsupported_backends=("rebar",),
            unsupported_backend_reason="known gap",
        ),
    )
    surface = fixture_parity_support.GroupedQuantifiedBytesSurfaceSpec(
        bundle=bundle,
        cases=cases,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        expected_module_search_texts_by_pattern={
            rb"a((b|c)+)\2d": frozenset({b"zzabbdzz"}),
            rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d": frozenset({b"zzaccdzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            rb"a((b|c)+)\2d": frozenset({b"accd", b"abbbd", b"abcd"}),
            rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d": frozenset(
                {b"abbd", b"abccd", b"acbd"}
            ),
        },
        expected_unsupported_backends=("rebar",),
        expected_unsupported_backend_reason="known gap",
    )

    _, bundle_bytes_cases = (
        fixture_parity_support.assert_grouped_quantified_direct_bytes_surface_spec(
            surface,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )
    )

    assert len(bundle_bytes_cases) == 10
    assert {case.text_model for case in bundle_bytes_cases} == {"bytes"}
    assert {case.manifest_id for case in bundle_bytes_cases} == {
        "quantified-nested-group-alternation-branch-local-backreference-workflows"
    }


def test_grouped_quantified_bytes_surface_spec_accepts_generic_mixed_text_bundle_cases(
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT
        / "open_ended_quantified_group_alternation_conditional_workflows.py",
        pattern_extractor=case_pattern,
    )
    surface = fixture_parity_support.GroupedQuantifiedBytesSurfaceSpec(
        bundle=bundle,
        cases=fixture_parity_support.OPEN_ENDED_CONDITIONAL_BYTES_CASES,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 5,
            }
        ),
        expected_module_search_texts_by_pattern={
            rb"a((bc|de){1,})?(?(1)d|e)": frozenset(
                {b"zzaezz", b"zzabcdzz", b"zzadedzz"}
            ),
            rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)": frozenset(
                {b"zzaezz", b"zzadedzz", b"zzadedededzz"}
            ),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            rb"a((bc|de){1,})?(?(1)d|e)": frozenset(
                {b"abcded", b"abcbcded", b"abcde"}
            ),
            rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)": frozenset({b"abcbcded", b"ad"}),
        },
    )

    bundle_str_cases, bundle_bytes_cases = (
        fixture_parity_support.assert_mixed_text_model_case_pairs(bundle)
    )

    observed_str_cases, observed_bytes_cases = (
        fixture_parity_support.assert_grouped_quantified_bytes_surface_spec(
            surface,
            bundle_str_cases=bundle_str_cases,
            bundle_bytes_cases=bundle_bytes_cases,
        )
    )

    assert len(observed_str_cases) == len(observed_bytes_cases) == 13
    assert Counter(
        (case.operation, case.helper) for case in observed_bytes_cases
    ) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 6,
            ("pattern_call", "fullmatch"): 5,
        }
    )


def test_grouped_quantified_bytes_surface_spec_rejects_direct_follow_on_surface_drift(
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT / "open_ended_quantified_group_alternation_workflows.py",
        pattern_extractor=case_pattern,
    )
    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (bundle,),
            (bundle,),
        )
    )
    drifted_cases = (
        replace(
            fixture_parity_support.OPEN_ENDED_ALTERNATION_BYTES_CASES[0],
            search_matches=(b"zzdriftedzz",),
        ),
        fixture_parity_support.OPEN_ENDED_ALTERNATION_BYTES_CASES[1],
    )
    surface = fixture_parity_support.GroupedQuantifiedBytesSurfaceSpec(
        bundle=bundle,
        cases=drifted_cases,
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
        expected_module_search_texts_by_pattern={
            rb"a(bc|de){1,}d": frozenset({b"zzabcdzz", b"zzadedzz"}),
            rb"a(?P<word>bc|de){1,}d": frozenset({b"zzabcdzz", b"zzadedzz"}),
        },
        expected_pattern_fullmatch_texts_by_pattern={
            rb"a(bc|de){1,}d": frozenset(
                {b"abcbcd", b"abcded", b"abcbcded", b"ad", b"abed"}
            ),
            rb"a(?P<word>bc|de){1,}d": frozenset(
                {b"abcded", b"abcbcded", b"adededed", b"ad", b"abed"}
            ),
        },
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "open-ended-quantified-group-alternation-workflows grouped quantified "
            "direct-bytes surface drifted; "
            "b'a(bc|de){1,}d' search texts drifted"
        ),
    ):
        fixture_parity_support.assert_grouped_quantified_direct_bytes_surface_spec(
            surface,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )


def test_assert_direct_bytes_follow_on_bundle_routing_accepts_mixed_manifest_buckets(
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    bundle = build_selected_fixture_bundle(fixture_path)
    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (bundle,),
            (bundle,),
        )
    )

    bundle_str_cases, bundle_bytes_cases = (
        fixture_parity_support.assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )
    )

    assert len(bundle_str_cases) == len(bundle_bytes_cases) == len(bundle.cases) // 2
    assert {case.text_model for case in bundle_str_cases} == {"str"}
    assert {case.text_model for case in bundle_bytes_cases} == {"bytes"}
    assert Counter((case.operation, case.helper) for case in bundle_str_cases) == Counter(
        (case.operation, case.helper) for case in bundle_bytes_cases
    )
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }


def test_assert_direct_bytes_follow_on_bundle_routing_rejects_bytes_left_in_generic_bucket(
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    bundle = build_selected_fixture_bundle(fixture_path)
    compile_cases = fixture_cases_for_operation((bundle,), "compile")
    module_cases = tuple(
        case
        for case in fixture_cases_for_operation((bundle,), "module_call")
        if case.text_model == "str"
    )
    pattern_cases = tuple(
        case
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
        if case.text_model == "str"
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "quantified-alternation-open-ended-workflows direct bytes follow-on routing "
            "drifted; compile bucket unexpectedly includes bytes case ids "
        ),
    ):
        fixture_parity_support.assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )


@pytest.mark.parametrize(
    "operation",
    (
        pytest.param("compile", id="compile"),
        pytest.param("module_call", id="module-call"),
        pytest.param("pattern_call", id="pattern-call"),
    ),
)
def test_assert_direct_bytes_follow_on_bundle_routing_rejects_unexpected_str_rows(
    operation: str,
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    bundle = build_selected_fixture_bundle(fixture_path)
    cases_by_operation = {
        bucket_operation: tuple(
            case
            for case in fixture_cases_for_operation((bundle,), bucket_operation)
            if case.text_model == "str"
        )
        for bucket_operation in ("compile", "module_call", "pattern_call")
    }
    assert cases_by_operation[operation]

    unexpected_case_id = f"unexpected-{operation}-str-case-id"
    cases_by_operation[operation] = (
        *cases_by_operation[operation],
        replace(cases_by_operation[operation][0], case_id=unexpected_case_id),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "quantified-alternation-open-ended-workflows direct bytes follow-on routing "
            f"drifted; {operation} bucket str case ids drifted; missing case ids: (); "
            f"unexpected case ids: ('{unexpected_case_id}',)"
        ),
    ):
        fixture_parity_support.assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=cases_by_operation["compile"],
            module_cases=cases_by_operation["module_call"],
            pattern_cases=cases_by_operation["pattern_call"],
        )


def test_assert_direct_bytes_follow_on_bundle_routing_rejects_missing_str_rows() -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    bundle = build_selected_fixture_bundle(fixture_path)
    compile_cases = tuple(
        case
        for case in fixture_cases_for_operation((bundle,), "compile")
        if case.text_model == "str"
    )[1:]
    module_cases = tuple(
        case
        for case in fixture_cases_for_operation((bundle,), "module_call")
        if case.text_model == "str"
    )
    pattern_cases = tuple(
        case
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
        if case.text_model == "str"
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "quantified-alternation-open-ended-workflows direct bytes follow-on routing "
            "drifted; compile bucket str case ids drifted; missing case ids: "
        ),
    ):
        fixture_parity_support.assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )


def test_assert_direct_bytes_follow_on_bundle_routing_rejects_str_only_manifest_bundle(
) -> None:
    fixture_path = CORRECTNESS_FIXTURES_ROOT / "grouped_match_workflows.py"
    bundle = build_selected_fixture_bundle(fixture_path)

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows direct bytes follow-on routing requires both "
            "str and bytes rows"
        ),
    ):
        fixture_parity_support.assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=fixture_cases_for_operation((bundle,), "compile"),
            module_cases=fixture_cases_for_operation((bundle,), "module_call"),
            pattern_cases=fixture_cases_for_operation((bundle,), "pattern_call"),
        )


def test_partition_direct_bytes_follow_on_case_buckets_drops_only_follow_on_bytes_rows(
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    bundle = build_selected_fixture_bundle(fixture_path)
    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (bundle,),
            (bundle,),
        )
    )

    for operation, bucket_cases in (
        ("compile", compile_cases),
        ("module_call", module_cases),
        ("pattern_call", pattern_cases),
    ):
        original_cases = fixture_cases_for_operation((bundle,), operation)
        expected_case_ids = tuple(
            case.case_id for case in original_cases if case.text_model == "str"
        )
        assert {case.text_model for case in original_cases} == {"bytes", "str"}
        assert {case.text_model for case in bucket_cases} == {"str"}
        assert tuple(case.case_id for case in bucket_cases) == expected_case_ids


def test_partition_direct_bytes_follow_on_case_buckets_preserves_unrelated_bytes_rows(
) -> None:
    follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    preserved_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    follow_on_bundle, preserved_bundle = tuple(
        build_selected_fixture_bundle(path)
        for path in (follow_on_fixture_path, preserved_fixture_path)
    )

    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (follow_on_bundle, preserved_bundle),
            (follow_on_bundle,),
        )
    )

    for operation, bucket_cases in (
        ("compile", compile_cases),
        ("module_call", module_cases),
        ("pattern_call", pattern_cases),
    ):
        expected_case_ids = tuple(
            case.case_id
            for case in fixture_cases_for_operation(
                (follow_on_bundle, preserved_bundle),
                operation,
            )
            if case.text_model != "bytes"
            or case.manifest_id != follow_on_bundle.manifest.manifest_id
        )
        bucket_case_ids = {case.case_id for case in bucket_cases}
        assert tuple(case.case_id for case in bucket_cases) == expected_case_ids
        assert {
            case.case_id
            for case in preserved_bundle.cases
            if case.operation == operation and case.text_model == "bytes"
        }.issubset(bucket_case_ids)
        assert {
            case.case_id
            for case in follow_on_bundle.cases
            if case.operation == operation and case.text_model == "bytes"
        }.isdisjoint(bucket_case_ids)


def test_partition_direct_bytes_follow_on_case_buckets_drops_bytes_rows_for_multiple_follow_on_manifests(
) -> None:
    first_follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    preserved_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_workflows.py"
    )
    second_follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    first_follow_on_bundle, preserved_bundle, second_follow_on_bundle = tuple(
        build_selected_fixture_bundle(path)
        for path in (
            first_follow_on_fixture_path,
            preserved_fixture_path,
            second_follow_on_fixture_path,
        )
    )
    follow_on_manifest_ids = frozenset(
        {
            first_follow_on_bundle.manifest.manifest_id,
            second_follow_on_bundle.manifest.manifest_id,
        }
    )

    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (first_follow_on_bundle, preserved_bundle, second_follow_on_bundle),
            (first_follow_on_bundle, second_follow_on_bundle),
        )
    )

    for operation, bucket_cases in (
        ("compile", compile_cases),
        ("module_call", module_cases),
        ("pattern_call", pattern_cases),
    ):
        expected_case_ids = tuple(
            case.case_id
            for case in fixture_cases_for_operation(
                (
                    first_follow_on_bundle,
                    preserved_bundle,
                    second_follow_on_bundle,
                ),
                operation,
            )
            if case.text_model != "bytes"
            or case.manifest_id not in follow_on_manifest_ids
        )
        bucket_case_ids = {case.case_id for case in bucket_cases}
        assert tuple(case.case_id for case in bucket_cases) == expected_case_ids
        assert {
            case.case_id
            for case in preserved_bundle.cases
            if case.operation == operation and case.text_model == "bytes"
        }.issubset(bucket_case_ids)
        assert {
            case.case_id
            for case in first_follow_on_bundle.cases
            if case.operation == operation and case.text_model == "bytes"
        }.isdisjoint(bucket_case_ids)
        assert {
            case.case_id
            for case in second_follow_on_bundle.cases
            if case.operation == operation and case.text_model == "bytes"
        }.isdisjoint(bucket_case_ids)


def test_direct_test_case_id_buckets_for_follow_on_bundles_keeps_shared_and_bytes_rows_separate(
) -> None:
    follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    preserved_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    follow_on_bundle, preserved_bundle = tuple(
        build_selected_fixture_bundle(path)
        for path in (follow_on_fixture_path, preserved_fixture_path)
    )

    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (follow_on_bundle, preserved_bundle),
            (follow_on_bundle,),
        )
    )

    assert fixture_parity_support.direct_test_case_id_buckets_for_follow_on_bundles(
        compile_cases=compile_cases,
        module_cases=module_cases,
        pattern_cases=pattern_cases,
        module_bucket_label="shared-module-search",
        pattern_bucket_label="shared-pattern-fullmatch",
        follow_on_buckets=(("open-ended-bytes-follow-on", follow_on_bundle),),
    ) == {
        "shared-compile": frozenset(case.case_id for case in compile_cases),
        "shared-module-search": frozenset(case.case_id for case in module_cases),
        "shared-pattern-fullmatch": frozenset(case.case_id for case in pattern_cases),
        "open-ended-bytes-follow-on": frozenset(
            case.case_id for case in follow_on_bundle.cases if case.text_model == "bytes"
        ),
    }


def test_direct_test_case_id_buckets_for_follow_on_bundles_collects_multiple_follow_on_manifests(
) -> None:
    first_follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    preserved_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_workflows.py"
    )
    second_follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    first_follow_on_bundle, preserved_bundle, second_follow_on_bundle = tuple(
        build_selected_fixture_bundle(path)
        for path in (
            first_follow_on_fixture_path,
            preserved_fixture_path,
            second_follow_on_fixture_path,
        )
    )

    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (first_follow_on_bundle, preserved_bundle, second_follow_on_bundle),
            (first_follow_on_bundle, second_follow_on_bundle),
        )
    )

    assert fixture_parity_support.direct_test_case_id_buckets_for_follow_on_bundles(
        compile_cases=compile_cases,
        module_cases=module_cases,
        pattern_cases=pattern_cases,
        module_bucket_label="shared-module-search",
        pattern_bucket_label="shared-pattern-fullmatch",
        follow_on_buckets=(
            ("open-ended-bytes-follow-on", first_follow_on_bundle),
            (
                "broader-range-conditional-bytes-follow-on",
                second_follow_on_bundle,
            ),
        ),
    ) == {
        "shared-compile": frozenset(case.case_id for case in compile_cases),
        "shared-module-search": frozenset(case.case_id for case in module_cases),
        "shared-pattern-fullmatch": frozenset(case.case_id for case in pattern_cases),
        "open-ended-bytes-follow-on": frozenset(
            case.case_id
            for case in first_follow_on_bundle.cases
            if case.text_model == "bytes"
        ),
        "broader-range-conditional-bytes-follow-on": frozenset(
            case.case_id
            for case in second_follow_on_bundle.cases
            if case.text_model == "bytes"
        ),
    }


def test_published_bytes_texts_by_pattern_separates_search_and_fullmatch_rows(
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    bundle = build_selected_fixture_bundle(fixture_path)
    compile_cases, module_cases, pattern_cases = (
        fixture_parity_support.partition_direct_bytes_follow_on_case_buckets(
            (bundle,),
            (bundle,),
        )
    )
    _, bundle_bytes_cases = fixture_parity_support.assert_direct_bytes_follow_on_bundle_routing(
        bundle,
        compile_cases=compile_cases,
        module_cases=module_cases,
        pattern_cases=pattern_cases,
    )

    assert fixture_parity_support.published_bytes_texts_by_pattern(bundle_bytes_cases) == (
        {
            rb"a(b|c){1,}d": frozenset({b"zzabdzz", b"zzacdzz"}),
            rb"a(?P<word>b|c){1,}d": frozenset({b"zzabdzz", b"zzacdzz"}),
        },
        {
            rb"a(b|c){1,}d": frozenset(
                {b"abcd", b"abccd", b"abcbcd", b"ad", b"abed"}
            ),
            rb"a(?P<word>b|c){1,}d": frozenset(
                {b"abcd", b"abccd", b"abcbcd", b"ad", b"abed"}
            ),
        },
    )


def test_published_bytes_texts_by_pattern_deduplicates_texts_and_handles_compiled_module_rows(
) -> None:
    compile_case = SimpleNamespace(
        operation="compile",
        pattern="placeholder",
        args=(),
        pattern_payload=lambda: b"ignored-by-compile",
    )
    module_case = SimpleNamespace(
        operation="module_call",
        helper="search",
        pattern="placeholder",
        args=(b"shared-pattern", b"shared-text"),
        pattern_payload=lambda: b"shared-pattern",
        use_compiled_pattern=False,
    )
    compiled_module_case = SimpleNamespace(
        operation="module_call",
        helper="search",
        pattern="placeholder",
        args=(b"compiled-text",),
        pattern_payload=lambda: b"shared-pattern",
        use_compiled_pattern=True,
    )
    pattern_case = SimpleNamespace(
        operation="pattern_call",
        helper="fullmatch",
        pattern="placeholder",
        args=(b"fullmatch-text",),
        pattern_payload=lambda: b"shared-pattern",
    )

    assert fixture_parity_support.published_bytes_texts_by_pattern(
        (
            compile_case,
            module_case,
            module_case,
            compiled_module_case,
            compiled_module_case,
            pattern_case,
            pattern_case,
        )
    ) == (
        {b"shared-pattern": frozenset({b"shared-text", b"compiled-text"})},
        {b"shared-pattern": frozenset({b"fullmatch-text"})},
    )


@pytest.mark.parametrize(
    ("case", "expected_message"),
    (
        pytest.param(
            SimpleNamespace(
                operation="module_call",
                helper="match",
                pattern="placeholder",
                args=(b"shared-pattern", b"module-text"),
                pattern_payload=lambda: b"shared-pattern",
                use_compiled_pattern=False,
            ),
            "published bytes texts expect module search rows",
            id="module-helper",
        ),
        pytest.param(
            SimpleNamespace(
                operation="pattern_call",
                helper="search",
                pattern="placeholder",
                args=(b"pattern-text",),
                pattern_payload=lambda: b"shared-pattern",
                use_compiled_pattern=False,
            ),
            "published bytes texts expect pattern fullmatch rows",
            id="pattern-helper",
        ),
        pytest.param(
            SimpleNamespace(
                operation="module_scan",
                helper="search",
                pattern="placeholder",
                args=(b"shared-pattern", b"module-text"),
                pattern_payload=lambda: b"shared-pattern",
                use_compiled_pattern=False,
            ),
            "published bytes texts encountered unsupported operation",
            id="operation",
        ),
    ),
)
def test_published_bytes_texts_by_pattern_rejects_unexpected_rows(
    case: SimpleNamespace,
    expected_message: str,
) -> None:
    with pytest.raises(AssertionError, match=expected_message):
        fixture_parity_support.published_bytes_texts_by_pattern((case,))


@pytest.mark.parametrize(
    "drift_kind",
    (
        pytest.param("fixture-path", id="fixture-path"),
        pytest.param("ordered-case-ids", id="ordered-case-ids"),
        pytest.param("expected-case-ids", id="expected-case-ids"),
        pytest.param("patterns", id="patterns"),
        pytest.param("text-models", id="text-models"),
        pytest.param("operation-helper-counts", id="operation-helper-counts"),
    ),
)
def test_assert_fixture_bundle_contract_rejects_contract_drift(
    tmp_path: pathlib.Path,
    drift_kind: str,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    str_bundle, mixed_bundle = tuple(
        build_selected_fixture_bundle(path) for path in (str_path, mixed_path)
    )

    bundle: FixtureBundle
    pattern_extractor = case_pattern
    expected_fixture_path = mixed_path
    expected_ordered_case_ids: tuple[str, ...] | None = None

    if drift_kind == "fixture-path":
        bundle = str_bundle
        pattern_extractor = str_case_pattern
        expected_fixture_path = mixed_path
        expected_ordered_case_ids = tuple(case.case_id for case in str_bundle.cases)
    elif drift_kind == "ordered-case-ids":
        bundle = str_bundle
        pattern_extractor = str_case_pattern
        expected_fixture_path = str_path
        expected_ordered_case_ids = tuple(
            reversed(tuple(case.case_id for case in str_bundle.cases))
        )
    elif drift_kind == "expected-case-ids":
        bundle = replace(
            str_bundle,
            expected_case_ids=frozenset(
                {
                    "bundle-loader-contract-compile-str",
                    "bundle-loader-contract-module-search-str",
                    "unexpected-case-id",
                }
            ),
        )
        pattern_extractor = str_case_pattern
        expected_fixture_path = str_path
        expected_ordered_case_ids = tuple(case.case_id for case in str_bundle.cases)
    elif drift_kind == "patterns":
        bundle = replace(
            str_bundle,
            expected_patterns=frozenset({r"unexpected-pattern"}),
        )
        pattern_extractor = str_case_pattern
        expected_fixture_path = str_path
        expected_ordered_case_ids = tuple(case.case_id for case in str_bundle.cases)
    elif drift_kind == "text-models":
        bundle = replace(mixed_bundle, expected_text_models=frozenset({"str"}))
        expected_fixture_path = mixed_path
        expected_ordered_case_ids = tuple(case.case_id for case in mixed_bundle.cases)
    elif drift_kind == "operation-helper-counts":
        bundle = replace(
            mixed_bundle,
            expected_operation_helper_counts=Counter(
                {
                    ("compile", None): 1,
                    ("module_call", "search"): 1,
                    ("pattern_call", "fullmatch"): 2,
                }
            ),
        )
        expected_fixture_path = mixed_path
        expected_ordered_case_ids = tuple(case.case_id for case in mixed_bundle.cases)
    else:
        raise AssertionError(f"unexpected drift_kind {drift_kind!r}")

    with pytest.raises(AssertionError):
        assert_fixture_bundle_contract(
            bundle,
            pattern_extractor=pattern_extractor,
            expected_fixture_path=expected_fixture_path,
            expected_ordered_case_ids=expected_ordered_case_ids,
        )


def test_assert_fixture_bundle_contract_rejects_duplicate_case_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    duplicate_case = str_bundle.cases[0]
    duplicate_bundle = FixtureBundle(
        manifest=str_bundle.manifest,
        cases=(duplicate_case, duplicate_case),
        expected_patterns=frozenset({str_case_pattern(duplicate_case)}),
        expected_operation_helper_counts=Counter(
            {(duplicate_case.operation, duplicate_case.helper): 2}
        ),
        expected_text_models=frozenset({duplicate_case.text_model}),
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"{duplicate_bundle.expected_manifest_id} bundle contains duplicate case ids: "
            f"('{duplicate_case.case_id}',)"
        ),
    ):
        assert_fixture_bundle_contract(
            duplicate_bundle,
            pattern_extractor=str_case_pattern,
            expected_fixture_path=str_bundle.manifest.path,
            expected_ordered_case_ids=(duplicate_case.case_id, duplicate_case.case_id),
        )


def test_selected_fixture_bundle_preserves_requested_order(
    tmp_path: pathlib.Path,
) -> None:
    selected_case_ids = (
        "bundle-loader-contract-compile-str",
        "bundle-loader-contract-pattern-search-str",
    )
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=selected_case_ids,
        pattern_extractor=str_case_pattern,
    )
    compile_cases = fixture_cases_for_operation((bundle,), "compile")
    pattern_cases = fixture_cases_for_operation((bundle,), "pattern_call")

    assert bundle.expected_case_ids == frozenset(selected_case_ids)
    assert bundle.expected_text_models == frozenset({"str"})
    assert tuple(case.case_id for case in compile_cases) == (
        "bundle-loader-contract-compile-str",
    )
    assert tuple(case.case_id for case in pattern_cases) == (
        "bundle-loader-contract-pattern-search-str",
    )
    assert fixture_cases_for_operation((bundle,), "module_call") == ()
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
        expected_ordered_case_ids=selected_case_ids,
    )


def test_selected_mixed_text_fixture_bundle_preserves_requested_order_and_text_models(
    tmp_path: pathlib.Path,
) -> None:
    selected_case_ids = (
        "bundle-loader-contract-mixed-pattern-fullmatch-bytes",
        "bundle-loader-contract-mixed-module-search-str",
    )
    _, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=selected_case_ids,
        pattern_extractor=case_pattern,
    )

    assert bundle.expected_case_ids == frozenset(selected_case_ids)
    assert bundle.expected_text_models == frozenset({"bytes", "str"})
    assert fixture_cases_for_operation((bundle,), "compile") == ()
    assert tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), "module_call")
    ) == ("bundle-loader-contract-mixed-module-search-str",)
    assert tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), "pattern_call")
    ) == ("bundle-loader-contract-mixed-pattern-fullmatch-bytes",)
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=mixed_path,
        expected_ordered_case_ids=selected_case_ids,
    )


def test_fixture_cases_for_operation_preserves_bundle_order_and_selected_rows(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-compile-bytes",
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-str",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )

    assert tuple(
        case.case_id
        for case in fixture_cases_for_operation((mixed_bundle, str_bundle), "compile")
    ) == (
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-mixed-compile-str",
        "bundle-loader-contract-compile-str",
    )
    assert tuple(
        case.case_id
        for case in fixture_cases_for_operation((mixed_bundle, str_bundle), "module_call")
    ) == ("bundle-loader-contract-mixed-module-search-str",)
    assert tuple(
        case.case_id
        for case in fixture_cases_for_operation((mixed_bundle, str_bundle), "pattern_call")
    ) == ("bundle-loader-contract-pattern-search-str",)
    assert fixture_cases_for_operation((mixed_bundle, str_bundle), "cache_workflow") == ()


def test_fixture_cases_for_operation_accepts_one_shot_bundle_iterables(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-compile-bytes",
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-str",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )

    bundle_iterable = (
        bundle for bundle in (mixed_bundle, str_bundle) if bundle.expected_case_ids is not None
    )

    assert tuple(
        case.case_id for case in fixture_cases_for_operation(bundle_iterable, "compile")
    ) == (
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-mixed-compile-str",
        "bundle-loader-contract-compile-str",
    )


def test_generated_specs_by_manifest_id_preserves_order_and_owner_labelled_lookup_failures(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-compile-bytes",
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-str",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )
    specs = (
        SimpleNamespace(bundle=mixed_bundle, owner="mixed"),
        SimpleNamespace(bundle=str_bundle, owner="str"),
    )

    specs_by_manifest_id = fixture_parity_support.generated_specs_by_manifest_id(specs)

    assert tuple(specs_by_manifest_id) == (
        "bundle-loader-contract-mixed",
        "bundle-loader-contract-str",
    )
    assert (
        fixture_parity_support.generated_spec_by_manifest_id(
            specs_by_manifest_id,
            mixed_bundle.expected_manifest_id,
            owner_label="generated contract",
        )
        is specs[0]
    )
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "unexpected generated contract manifest id "
            "'bundle-loader-contract-missing'"
        ),
    ):
        fixture_parity_support.generated_spec_by_manifest_id(
            specs_by_manifest_id,
            "bundle-loader-contract-missing",
            owner_label="generated contract",
        )


def test_generated_compile_anchor_case_selection_preserves_flattened_order_across_bundles(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-compile-bytes",
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-str",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )
    specs = (
        SimpleNamespace(bundle=mixed_bundle),
        SimpleNamespace(bundle=str_bundle),
    )

    assert tuple(
        case.case_id
        for case in fixture_cases_for_operation(
            tuple(spec.bundle for spec in specs),
            "compile",
        )
    ) == (
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-mixed-compile-str",
        "bundle-loader-contract-compile-str",
    )


def test_generated_compile_anchor_helpers_preserve_representative_spec_contract_inputs(
    tmp_path: pathlib.Path,
) -> None:
    _, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-compile-bytes",
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-str",
        ),
        pattern_extractor=case_pattern,
    )
    spec = SimpleNamespace(
        bundle=mixed_bundle,
        expected_compile_case_ids=(
            "bundle-loader-contract-mixed-compile-bytes",
            "bundle-loader-contract-mixed-compile-str",
        ),
        expected_patterns=frozenset({b"a(bc|de){1,}d", r"a(bc|de){1,}d"}),
        expected_text_models=frozenset({"bytes", "str"}),
    )
    specs_by_manifest_id = fixture_parity_support.generated_specs_by_manifest_id((spec,))
    compile_cases = fixture_cases_for_operation((spec.bundle,), "compile")

    assert (
        fixture_parity_support.generated_spec_by_manifest_id(
            specs_by_manifest_id,
            mixed_bundle.expected_manifest_id,
            owner_label="generated representative",
        )
        is spec
    )
    assert tuple(case.case_id for case in compile_cases) == spec.expected_compile_case_ids
    assert {case_pattern(case) for case in compile_cases} == spec.expected_patterns
    assert {case.text_model for case in compile_cases} == spec.expected_text_models


def test_fixture_cases_by_id_preserves_input_order_for_bundles_and_cases(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-bytes",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )

    bundles_by_id = fixture_cases_by_id((mixed_bundle, str_bundle))
    assert tuple(bundles_by_id) == (
        "bundle-loader-contract-mixed-module-search-str",
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-pattern-search-str",
        "bundle-loader-contract-compile-str",
    )

    cases_by_id = fixture_cases_by_id(str_bundle.cases)
    assert tuple(cases_by_id) == (
        "bundle-loader-contract-pattern-search-str",
        "bundle-loader-contract-compile-str",
    )
    assert cases_by_id["bundle-loader-contract-compile-str"] is str_bundle.cases[1]


def test_flatten_fixture_bundles_preserves_bundle_and_case_order(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-bytes",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )

    assert tuple(case.case_id for case in flatten_fixture_bundles((mixed_bundle, str_bundle))) == (
        "bundle-loader-contract-mixed-module-search-str",
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-pattern-search-str",
        "bundle-loader-contract-compile-str",
    )


def test_ordered_fixture_bundle_case_ids_preserve_bundle_and_case_order(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-bytes",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )

    assert ordered_fixture_bundle_case_ids((mixed_bundle, str_bundle)) == (
        "bundle-loader-contract-mixed-module-search-str",
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-pattern-search-str",
        "bundle-loader-contract-compile-str",
    )


def test_ordered_fixture_bundle_case_ids_match_flattened_case_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-bytes",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )
    bundles = (mixed_bundle, str_bundle)

    assert ordered_fixture_bundle_case_ids(bundles) == tuple(
        case.case_id for case in flatten_fixture_bundles(bundles)
    )


def test_fixture_cases_by_id_accepts_mixed_bundle_and_case_entries(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    mixed_bundle = build_selected_fixture_bundle(
        mixed_path,
        selected_case_ids=(
            "bundle-loader-contract-mixed-module-search-str",
            "bundle-loader-contract-mixed-compile-bytes",
        ),
        pattern_extractor=case_pattern,
    )
    str_bundle = build_selected_fixture_bundle(
        str_path,
        selected_case_ids=(
            "bundle-loader-contract-pattern-search-str",
            "bundle-loader-contract-compile-str",
        ),
        pattern_extractor=str_case_pattern,
    )

    cases_by_id = fixture_cases_by_id((mixed_bundle, str_bundle.cases[1]))

    assert tuple(cases_by_id) == (
        "bundle-loader-contract-mixed-module-search-str",
        "bundle-loader-contract-mixed-compile-bytes",
        "bundle-loader-contract-compile-str",
    )
    assert (
        cases_by_id["bundle-loader-contract-mixed-module-search-str"]
        is mixed_bundle.cases[0]
    )
    assert cases_by_id["bundle-loader-contract-compile-str"] is str_bundle.cases[1]


def test_fixture_cases_by_id_rejects_non_fixture_entries(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = build_selected_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )

    with pytest.raises(
        TypeError,
        match=re.escape(
            "fixture_cases_by_id() accepts FixtureBundle or FixtureCase entries, "
            "got FixtureManifest"
        ),
    ):
        fixture_cases_by_id((bundle, bundle.manifest))


def test_fixture_cases_by_id_rejects_duplicate_case_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = build_selected_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )
    duplicate_case = replace(bundle.cases[1], case_id=bundle.cases[0].case_id)

    with pytest.raises(
        ValueError,
        match=(
            "fixture cases contain duplicate case ids: "
            r"\('bundle-loader-contract-compile-str',\)"
        ),
    ):
        fixture_cases_by_id((bundle.cases[0], duplicate_case))


def test_full_manifest_bundle_sets_str_text_model_expectation(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = _load_full_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )

    assert bundle.expected_case_ids is None
    assert bundle.expected_text_models == frozenset({"str"})
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
    )


def test_assert_fixture_bundle_tracks_published_case_frontier_accepts_selected_and_uncovered_rows(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids

    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=(published_case_ids[0], published_case_ids[2]),
        expected_uncovered_case_ids=(published_case_ids[1],),
    )


def test_assert_fixture_bundle_tracks_published_case_frontier_accepts_selected_and_uncovered_rows_for_mixed_manifest(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_mixed_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids

    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=(published_case_ids[1], published_case_ids[3]),
        expected_uncovered_case_ids=(published_case_ids[0], published_case_ids[2]),
    )


def test_assert_fixture_bundle_tracks_published_case_frontier_rejects_empty_selected_case_ids(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"{bundle.expected_manifest_id} selected_case_ids must not be empty"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=(),
            expected_uncovered_case_ids=published_case_ids,
        )


@pytest.mark.parametrize("duplicate_source", ("selected", "uncovered"))
def test_assert_fixture_bundle_tracks_published_case_frontier_rejects_duplicate_case_ids(
    tmp_path: pathlib.Path,
    duplicate_source: str,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids

    if duplicate_source == "selected":
        selected_case_ids = (published_case_ids[0], published_case_ids[0])
        expected_uncovered_case_ids = (published_case_ids[1], published_case_ids[2])
        error_message = (
            f"{bundle.expected_manifest_id} selected_case_ids contain duplicate ids: "
            f"{(published_case_ids[0],)}"
        )
    elif duplicate_source == "uncovered":
        selected_case_ids = (published_case_ids[0],)
        expected_uncovered_case_ids = (
            published_case_ids[1],
            published_case_ids[1],
            published_case_ids[2],
        )
        error_message = (
            f"{bundle.expected_manifest_id} expected_uncovered_case_ids contain "
            f"duplicate ids: {(published_case_ids[1],)}"
        )
    else:
        raise AssertionError(f"unexpected duplicate_source {duplicate_source!r}")

    with pytest.raises(AssertionError, match=re.escape(error_message)):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=selected_case_ids,
            expected_uncovered_case_ids=expected_uncovered_case_ids,
        )


def test_assert_fixture_bundle_tracks_published_case_frontier_rejects_selected_uncovered_overlap(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids
    overlapping_case_id = published_case_ids[1]

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"{bundle.expected_manifest_id} selected and uncovered case ids overlap: "
            f"{(overlapping_case_id,)}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=(published_case_ids[0], overlapping_case_id),
            expected_uncovered_case_ids=(overlapping_case_id, published_case_ids[2]),
        )


def test_assert_fixture_bundle_tracks_published_case_frontier_rejects_missing_and_unexpected_rows(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids
    missing_case_id = "missing-case-id"

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"{bundle.expected_manifest_id} published frontier drifted; "
            f"missing published case ids: {(missing_case_id,)}; "
            f"unexpected published case ids: {published_case_ids[2:]}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=(published_case_ids[0],),
            expected_uncovered_case_ids=(published_case_ids[1], missing_case_id),
        )


def test_assert_fixture_bundle_tracks_published_case_frontier_rejects_uncovered_order_drift(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = bundle.published_case_ids
    expected_uncovered_case_ids = (published_case_ids[2], published_case_ids[1])

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"{bundle.expected_manifest_id} uncovered published case ids changed; "
            f"expected {expected_uncovered_case_ids}, "
            f"got {published_case_ids[1:]}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=(published_case_ids[0],),
            expected_uncovered_case_ids=expected_uncovered_case_ids,
        )


@pytest.mark.parametrize(
    ("selected_case_ids", "error_message"),
    (
        pytest.param(
            (),
            f"{BUNDLE_LOADER_CONTRACT_STR_FILENAME} selected_case_ids must not be empty",
            id="empty",
        ),
        pytest.param(
            (
                "bundle-loader-contract-compile-str",
                "bundle-loader-contract-compile-str",
            ),
            f"{BUNDLE_LOADER_CONTRACT_STR_FILENAME} selected_case_ids contains duplicate ids: "
            "('bundle-loader-contract-compile-str',)",
            id="duplicate",
        ),
        pytest.param(
            ("missing-case-id",),
            f"{BUNDLE_LOADER_CONTRACT_STR_FILENAME} is missing expected fixture rows: "
            "('missing-case-id',)",
            id="missing",
        ),
    ),
)
def test_selected_fixture_bundle_rejects_invalid_selected_case_ids(
    tmp_path: pathlib.Path,
    selected_case_ids: tuple[str, ...],
    error_message: str,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)

    with pytest.raises(ValueError, match=re.escape(error_message)):
        build_selected_fixture_bundle(
            str_path,
            selected_case_ids=selected_case_ids,
            pattern_extractor=str_case_pattern,
        )


@pytest.mark.parametrize(
    "selected_case_ids",
    (
        pytest.param(None, id="whole-manifest"),
        pytest.param(
            (BUNDLE_LOADER_CONTRACT_DUPLICATE_CASE_ID,),
            id="selected-subset",
        ),
    ),
)
def test_selected_fixture_bundle_rejects_duplicate_fixture_case_ids(
    tmp_path: pathlib.Path,
    selected_case_ids: tuple[str, ...] | None,
) -> None:
    fixture_path = _write_bundle_loader_contract_duplicate_fixture_module(tmp_path)

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"{BUNDLE_LOADER_CONTRACT_DUPLICATE_FILENAME} contains duplicate fixture case ids: "
            f"('{BUNDLE_LOADER_CONTRACT_DUPLICATE_CASE_ID}',)"
        ),
    ):
        build_selected_fixture_bundle(
            fixture_path,
            selected_case_ids=selected_case_ids,
            pattern_extractor=str_case_pattern,
        )


def test_fixture_case_pytest_id_returns_case_case_id() -> None:
    manifest = load_fixture_manifest(DEFAULT_FIXTURE_PATHS[0])
    case = manifest.cases[0]

    assert fixture_case_pytest_id(case) == case.case_id


def test_fixture_bundle_manifest_pytest_id_returns_bundle_expected_manifest_id() -> None:
    bundle = build_selected_fixture_bundle(
        DEFAULT_FIXTURE_PATHS[0],
        pattern_extractor=case_pattern,
    )

    assert fixture_bundle_manifest_pytest_id(bundle) == bundle.expected_manifest_id


def test_bundle_manifest_pytest_id_returns_spec_bundle_expected_manifest_id() -> None:
    bundle = build_selected_fixture_bundle(
        DEFAULT_FIXTURE_PATHS[0],
        pattern_extractor=case_pattern,
    )
    spec = SimpleNamespace(bundle=bundle)

    assert bundle_manifest_pytest_id(spec) == bundle.expected_manifest_id


def test_follow_on_pytest_id_returns_spec_follow_on_id() -> None:
    spec = SimpleNamespace(follow_on_id="direct-follow-on")

    assert follow_on_pytest_id(spec) == "direct-follow-on"


@pytest.mark.parametrize(
    ("case", "expected_id"),
    (
        pytest.param(
            SupplementalCase(id="supplemental-id", pattern=b"abc"),
            "supplemental-id",
            id="supplemental-case",
        ),
        pytest.param(
            BoundedPatternCase(
                id="bounded-pattern-id",
                pattern="abc",
                helper="search",
                string="zabc",
                bounds=(0, 4),
            ),
            "bounded-pattern-id",
            id="bounded-pattern-case",
        ),
        pytest.param(
            PatternTraceCase(
                id="trace-id",
                pattern="abc",
                search_text="zabc",
                fullmatch_text="abc",
            ),
            "trace-id",
            id="pattern-trace-case",
        ),
    ),
)
def test_id_attribute_pytest_id_returns_case_id_attribute(
    case: SupplementalCase | BoundedPatternCase | PatternTraceCase,
    expected_id: str,
) -> None:
    assert id_attribute_pytest_id(case) == expected_id


@pytest.mark.parametrize(
    "helper_name",
    (
        "compile_case_trace_prefix",
        "build_compile_case_pattern_trace_cases",
        "build_pattern_trace_cases",
    ),
)
def test_trace_helper_exports_stay_owner_local(helper_name: str) -> None:
    assert not hasattr(fixture_parity_support, helper_name)


def test_load_fixture_manifest_preserves_distinct_zero_flag_keyword_carriers(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_zero_flag_keyword_carrier_fixture_module(tmp_path)
    manifest = load_fixture_manifest(fixture_path)
    cases_by_id = records_by_string_id(manifest.cases, id_attr="case_id")

    assert tuple(cases_by_id) == (
        ZERO_FLAG_KEYWORD_NOFLAG_CASE_ID,
        ZERO_FLAG_KEYWORD_INT_ZERO_CASE_ID,
        ZERO_FLAG_KEYWORD_BOOL_FALSE_CASE_ID,
    )
    _assert_zero_flag_keyword_carrier(
        cases_by_id[ZERO_FLAG_KEYWORD_NOFLAG_CASE_ID],
        expected_type=re.RegexFlag,
    )
    _assert_zero_flag_keyword_carrier(
        cases_by_id[ZERO_FLAG_KEYWORD_INT_ZERO_CASE_ID],
        expected_type=int,
    )
    _assert_zero_flag_keyword_carrier(
        cases_by_id[ZERO_FLAG_KEYWORD_BOOL_FALSE_CASE_ID],
        expected_type=bool,
    )


def test_selected_fixture_bundle_preserves_zero_flag_keyword_carriers_and_order(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_zero_flag_keyword_carrier_fixture_module(tmp_path)
    selected_case_ids = (
        ZERO_FLAG_KEYWORD_BOOL_FALSE_CASE_ID,
        ZERO_FLAG_KEYWORD_NOFLAG_CASE_ID,
    )
    bundle = build_selected_fixture_bundle(
        fixture_path,
        selected_case_ids=selected_case_ids,
        pattern_extractor=case_pattern,
    )

    assert bundle.expected_case_ids == frozenset(selected_case_ids)
    assert tuple(case.case_id for case in bundle.cases) == selected_case_ids
    _assert_zero_flag_keyword_carrier(bundle.cases[0], expected_type=bool)
    _assert_zero_flag_keyword_carrier(bundle.cases[1], expected_type=re.RegexFlag)
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=fixture_path,
        expected_ordered_case_ids=selected_case_ids,
    )


@pytest.mark.parametrize(
    "pattern",
    (
        pytest.param(r"(?P<word>abc)", id="named-group-str"),
        pytest.param(b"abc", id="literal-bytes"),
    ),
)
def test_compile_with_cpython_parity_covers_representative_supported_patterns(
    regex_backend: tuple[str, object],
    pattern: str | bytes,
) -> None:
    backend_name, backend = regex_backend

    observed, expected = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )

    assert observed.pattern == expected.pattern == pattern
    if isinstance(pattern, str):
        assert observed.groupindex == expected.groupindex == {"word": 1}
    else:
        assert observed.groupindex == expected.groupindex == {}


def test_compile_with_cpython_parity_can_skip_cache_identity_for_supported_non_caching_backend() -> None:
    observed, expected = compile_with_cpython_parity(
        "stdlib",
        _NonCachingStdlibBackend(),
        "abc",
        check_cache_identity=False,
    )

    assert observed.pattern == expected.pattern == "abc"
    assert observed.flags == expected.flags == int(re.UNICODE)


def test_compile_with_cpython_parity_rejects_non_caching_backend_by_default() -> None:
    with pytest.raises(AssertionError):
        compile_with_cpython_parity(
            "stdlib",
            _NonCachingStdlibBackend(),
            "abc",
        )


@pytest.mark.parametrize(
    ("pattern", "flags", "expected_groups", "expected_groupindex"),
    (
        pytest.param("abc", 0, 0, {}, id="literal-str"),
        pytest.param(r"(?P<word>abc)", 0, 1, {"word": 1}, id="named-group-str"),
        pytest.param(b"abc", 0, 0, {}, id="literal-bytes"),
    ),
)
def test_pattern_parity_helper_accepts_supported_pattern_metadata(
    regex_backend: tuple[str, object],
    pattern: str | bytes,
    flags: int,
    expected_groups: int,
    expected_groupindex: dict[str, int],
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(pattern, flags)
    expected = re.compile(pattern, flags)

    assert_pattern_parity(backend_name, observed, expected)
    assert observed.groups == expected.groups == expected_groups
    assert observed.groupindex == expected.groupindex == expected_groupindex


def test_pattern_parity_helper_rejects_stdlib_patterns_for_rebar_backend() -> None:
    observed = re.compile("abc")
    expected = re.compile("abc")

    with pytest.raises(AssertionError):
        assert_pattern_parity("rebar", observed, expected)


@pytest.mark.parametrize(
    ("pattern", "flags", "mutator"),
    (
        pytest.param(
            "abc",
            0,
            lambda compiled: setattr(compiled, "pattern", "abd"),
            id="pattern-mismatch",
        ),
        pytest.param(
            "abc",
            0,
            lambda compiled: setattr(compiled, "flags", compiled.flags | int(re.IGNORECASE)),
            id="flags-mismatch",
        ),
        pytest.param(
            r"(?P<word>abc)",
            0,
            lambda compiled: setattr(compiled, "groups", compiled.groups + 1),
            id="groups-mismatch",
        ),
        pytest.param(
            r"(?P<word>abc)",
            0,
            lambda compiled: setattr(compiled, "groupindex", {"other": 1}),
            id="groupindex-mismatch",
        ),
    ),
)
def test_pattern_parity_helper_rejects_rebar_pattern_metadata_mismatches(
    pattern: str,
    flags: int,
    mutator,
) -> None:
    observed = rebar.compile(pattern, flags)
    expected = re.compile(pattern, flags)

    mutator(observed)

    with pytest.raises(AssertionError):
        assert_pattern_parity("rebar", observed, expected)


def test_value_parity_accepts_nested_builtin_results() -> None:
    assert_value_parity(
        ("alpha", [b"beta", ("gamma", 3)]),
        ("alpha", [b"beta", ("gamma", 3)]),
    )


def test_value_parity_accepts_nested_mapping_results_without_order_coupling() -> None:
    assert_value_parity(
        {
            "beta": (b"gamma", {"delta": 3}),
            "alpha": ["one", 2],
        },
        {
            "alpha": ["one", 2],
            "beta": (b"gamma", {"delta": 3}),
        },
    )


def test_value_parity_rejects_equal_top_level_values_with_different_types() -> None:
    with pytest.raises(AssertionError):
        assert_value_parity(True, 1)


def test_value_parity_rejects_equal_nested_values_with_different_types() -> None:
    class _StringSubclass(str):
        pass

    with pytest.raises(AssertionError):
        assert_value_parity(
            (["alpha"], (True,)),
            ([_StringSubclass("alpha")], (1,)),
        )


def test_value_parity_rejects_equal_mapping_values_with_different_types() -> None:
    with pytest.raises(AssertionError):
        assert_value_parity({"alpha": True}, {"alpha": 1})


def test_value_parity_rejects_equal_mapping_keys_with_different_types() -> None:
    with pytest.raises(AssertionError):
        assert_value_parity({True: "alpha"}, {1: "alpha"})


def test_value_parity_rejects_missing_mapping_keys_with_clear_error() -> None:
    with pytest.raises(
        AssertionError,
        match=r"missing mapping key parity for 'beta'",
    ):
        assert_value_parity({"alpha": 1}, {"alpha": 1, "beta": 2})


def test_value_parity_rejects_unexpected_mapping_keys_with_clear_error() -> None:
    with pytest.raises(
        AssertionError,
        match=r"unexpected mapping key parity for \('beta',\)",
    ):
        assert_value_parity({"alpha": 1, "beta": 2}, {"alpha": 1})


@pytest.mark.parametrize(
    "text",
    (
        pytest.param("abd", id="present-optional-group"),
        pytest.param("ad", id="missing-optional-group"),
    ),
)
@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-fullmatch"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_parity_helpers_cover_match_object_contracts(
    regex_backend: tuple[str, object],
    text: str,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _optional_named_group_match(
        backend_name,
        backend,
        text,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-search"),
        pytest.param(True, id="pattern-search"),
    ),
)
def test_match_parity_helpers_cover_zero_group_str_match_object_contracts(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _str_literal_search_match(
        backend_name,
        backend,
        "zzabczz",
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-search"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_convenience_api_parity_covers_multiple_named_groups(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _branch_local_named_backreference_match(
        backend_name,
        backend,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-search"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_convenience_api_parity_covers_multiple_named_groups_for_bytes_patterns(
    use_compiled_pattern: bool,
) -> None:
    observed, expected = _branch_local_named_backreference_bytes_match(
        "stdlib",
        re,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    assert_match_parity("stdlib", observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="mixed group tuple tracing requires rebar.Match",
)
@pytest.mark.parametrize(
    "text",
    (
        pytest.param("abd", id="present-optional-group"),
        pytest.param("ad", id="missing-optional-group"),
    ),
)
@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-fullmatch"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_parity_helper_checks_mixed_group_reference_tuples_for_named_groups(
    monkeypatch: pytest.MonkeyPatch,
    text: str,
    use_compiled_pattern: bool,
) -> None:
    observed, expected = _optional_named_group_match(
        "rebar",
        rebar,
        text,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    calls: list[tuple[object, ...]] = []
    original_group = rebar.Match.group

    def recording_group(self: rebar.Match, *groups: object) -> object:
        calls.append(groups)
        return original_group(self, *groups)

    monkeypatch.setattr(rebar.Match, "group", recording_group)

    assert_match_parity("rebar", observed, expected, check_regs=True)

    assert (0, False, 1) in calls
    assert (0, 1, "word") in calls


@pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="mixed group tuple tracing requires rebar.Match",
)
@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-search"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_parity_helper_checks_mixed_group_reference_tuples_for_multiple_names(
    monkeypatch: pytest.MonkeyPatch,
    use_compiled_pattern: bool,
) -> None:
    observed, expected = _branch_local_named_backreference_match(
        "rebar",
        rebar,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    calls: list[tuple[object, ...]] = []
    original_group = rebar.Match.group

    def recording_group(self: rebar.Match, *groups: object) -> object:
        calls.append(groups)
        return original_group(self, *groups)

    monkeypatch.setattr(rebar.Match, "group", recording_group)

    assert_match_parity("rebar", observed, expected, check_regs=True)

    assert (0, 1, "outer") in calls


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-search"),
        pytest.param(True, id="pattern-search"),
    ),
)
def test_match_parity_helpers_cover_bytes_match_object_contracts(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _bytes_literal_search_match(
        backend_name,
        backend,
        b"zzabczz",
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize(
    "text",
    (
        pytest.param(b"abd", id="present-optional-group"),
        pytest.param(b"ad", id="missing-optional-group"),
    ),
)
@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-fullmatch"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_parity_helpers_cover_bytes_named_group_match_object_contracts(
    text: bytes,
    use_compiled_pattern: bool,
) -> None:
    observed, expected = _optional_named_group_bytes_match(
        "stdlib",
        re,
        text,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is not None
    assert expected is not None

    assert_match_parity("stdlib", observed, expected, check_regs=True)
    assert_match_result_parity("stdlib", observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


def test_invalid_match_group_access_parity_handles_missing_name_collisions() -> None:
    match = re.fullmatch(r"(?P<missing>a)(?P<missing_group>b)", "ab")

    assert match is not None
    assert_invalid_match_group_access_parity(match, match)


@pytest.mark.parametrize(
    ("non_raising_accessor", "unexpected_result"),
    (
        pytest.param("group", "unexpected-group", id="group"),
        pytest.param("getitem", "unexpected-item", id="getitem"),
    ),
)
def test_invalid_match_group_access_parity_rejects_non_raising_accessors(
    non_raising_accessor: str,
    unexpected_result: object,
) -> None:
    expected_match = re.fullmatch(r"(?P<missing>a)(?P<missing_group>b)", "ab")

    assert expected_match is not None

    class _UnexpectedlyPermissiveMatch:
        def __init__(self, wrapped_match: re.Match[str]) -> None:
            self.re = wrapped_match.re
            self._wrapped_match = wrapped_match

        def group(self, reference: object) -> object:
            if non_raising_accessor == "group":
                return unexpected_result
            return self._wrapped_match.group(reference)

        def span(self, reference: object) -> tuple[int, int]:
            return self._wrapped_match.span(reference)

        def start(self, reference: object) -> int:
            return self._wrapped_match.start(reference)

        def end(self, reference: object) -> int:
            return self._wrapped_match.end(reference)

        def __getitem__(self, reference: object) -> object:
            if non_raising_accessor == "getitem":
                return unexpected_result
            return self._wrapped_match[reference]

    permissive_match = _UnexpectedlyPermissiveMatch(expected_match)

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"expected {non_raising_accessor}(-1) to raise for "
            f"{expected_match.re.pattern!r}"
        ),
    ):
        assert_invalid_match_group_access_parity(permissive_match, expected_match)


class _GeneratedMatrixBackendContract:
    def __init__(self, label: str) -> None:
        self.label = label

    def search(self, pattern: str | bytes, text: str | bytes) -> str:
        return f"{self.label}.search({pattern!r}, {text!r})"

    def match(self, pattern: str | bytes, text: str | bytes) -> str:
        return f"{self.label}.match({pattern!r}, {text!r})"

    def fullmatch(self, pattern: str | bytes, text: str | bytes) -> str:
        return f"{self.label}.fullmatch({pattern!r}, {text!r})"


class _GeneratedMatrixPatternContract:
    def __init__(self, label: str) -> None:
        self.label = label

    def search(self, text: str | bytes) -> str:
        return f"{self.label}.search({text!r})"

    def match(self, text: str | bytes) -> str:
        return f"{self.label}.match({text!r})"

    def fullmatch(self, text: str | bytes) -> str:
        return f"{self.label}.fullmatch({text!r})"


class _GeneratedNoMatchPatternContract:
    def search(self, text: str | bytes) -> None:
        return None

    def match(self, text: str | bytes) -> None:
        return None

    def fullmatch(self, text: str | bytes) -> None:
        return None


def _generated_matrix_case_contract(
    pattern: str | bytes,
    *,
    flags: int = 0,
) -> SimpleNamespace:
    return SimpleNamespace(
        pattern=pattern,
        args=(),
        flags=flags,
        pattern_payload=lambda: pattern,
    )


def test_assert_generated_text_matrix_matches_cpython_executes_module_and_pattern_matrix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compile_calls: list[tuple[str, str, int]] = []
    recorded_calls: list[tuple[str, object, object, bool]] = []
    regex_backend = ("stdlib", _GeneratedMatrixBackendContract("backend"))
    observed_pattern = _GeneratedMatrixPatternContract("observed-pattern")
    expected_pattern = _GeneratedMatrixPatternContract("expected-pattern")
    case = _generated_matrix_case_contract(r"a(b|c){1,2}d", flags=4)
    candidate_texts = ("zzabdzz", "zzacdzz")

    def _compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
        *,
        check_cache_identity: bool = True,
    ) -> tuple[object, object]:
        assert backend_name == "stdlib"
        assert backend is regex_backend[1]
        assert check_cache_identity is True
        compile_calls.append((backend_name, pattern, flags))
        return observed_pattern, expected_pattern

    def _record_result(
        backend_name: str,
        observed: object,
        expected: object,
        *,
        check_regs: bool = False,
    ) -> None:
        recorded_calls.append((backend_name, observed, expected, check_regs))

    monkeypatch.setattr(fixture_parity_support, "compile_with_cpython_parity", _compile)
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        _record_result,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        lambda observed, expected: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        lambda observed, expected: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        lambda observed, expected: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "search",
        lambda pattern, text: f"cpython.search({pattern!r}, {text!r})",
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "match",
        lambda pattern, text: f"cpython.match({pattern!r}, {text!r})",
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "fullmatch",
        lambda pattern, text: f"cpython.fullmatch({pattern!r}, {text!r})",
    )

    fixture_parity_support.assert_generated_text_matrix_matches_cpython(
        regex_backend,
        case,
        candidate_texts=candidate_texts,
        pattern_extractor=str_case_pattern,
        failure_prefix="generated matrix drifted",
    )

    assert compile_calls == [("stdlib", r"a(b|c){1,2}d", 4)]
    assert recorded_calls == [
        (
            "stdlib",
            "backend.search('a(b|c){1,2}d', 'zzabdzz')",
            "cpython.search('a(b|c){1,2}d', 'zzabdzz')",
            True,
        ),
        (
            "stdlib",
            "observed-pattern.search('zzabdzz')",
            "expected-pattern.search('zzabdzz')",
            True,
        ),
        (
            "stdlib",
            "backend.match('a(b|c){1,2}d', 'zzabdzz')",
            "cpython.match('a(b|c){1,2}d', 'zzabdzz')",
            True,
        ),
        (
            "stdlib",
            "observed-pattern.match('zzabdzz')",
            "expected-pattern.match('zzabdzz')",
            True,
        ),
        (
            "stdlib",
            "backend.fullmatch('a(b|c){1,2}d', 'zzabdzz')",
            "cpython.fullmatch('a(b|c){1,2}d', 'zzabdzz')",
            True,
        ),
        (
            "stdlib",
            "observed-pattern.fullmatch('zzabdzz')",
            "expected-pattern.fullmatch('zzabdzz')",
            True,
        ),
        (
            "stdlib",
            "backend.search('a(b|c){1,2}d', 'zzacdzz')",
            "cpython.search('a(b|c){1,2}d', 'zzacdzz')",
            True,
        ),
        (
            "stdlib",
            "observed-pattern.search('zzacdzz')",
            "expected-pattern.search('zzacdzz')",
            True,
        ),
        (
            "stdlib",
            "backend.match('a(b|c){1,2}d', 'zzacdzz')",
            "cpython.match('a(b|c){1,2}d', 'zzacdzz')",
            True,
        ),
        (
            "stdlib",
            "observed-pattern.match('zzacdzz')",
            "expected-pattern.match('zzacdzz')",
            True,
        ),
        (
            "stdlib",
            "backend.fullmatch('a(b|c){1,2}d', 'zzacdzz')",
            "cpython.fullmatch('a(b|c){1,2}d', 'zzacdzz')",
            True,
        ),
        (
            "stdlib",
            "observed-pattern.fullmatch('zzacdzz')",
            "expected-pattern.fullmatch('zzacdzz')",
            True,
        ),
    ]


def test_assert_generated_text_matrix_matches_cpython_skips_follow_on_checks_for_no_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regex_backend = ("stdlib", _GeneratedMatrixBackendContract("backend"))
    case = _generated_matrix_case_contract(r"a(b)?c(?(1)d|e){2}")
    candidate_texts = ("text-0",)
    recorded_calls: list[tuple[str, object, object, bool]] = []

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        lambda *args, **kwargs: (
            _GeneratedNoMatchPatternContract(),
            _GeneratedNoMatchPatternContract(),
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        lambda backend_name, observed, expected, *, check_regs=False: recorded_calls.append(
            (backend_name, observed, expected, check_regs)
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("unexpected convenience helper call")
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("unexpected valid-group-access helper call")
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("unexpected invalid-group-access helper call")
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "search",
        lambda pattern, text: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "match",
        lambda pattern, text: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "fullmatch",
        lambda pattern, text: None,
    )

    fixture_parity_support.assert_generated_text_matrix_matches_cpython(
        regex_backend,
        case,
        candidate_texts=candidate_texts,
        pattern_extractor=str_case_pattern,
        failure_prefix="generated no-match drifted",
    )

    assert recorded_calls == [
        ("stdlib", "backend.search('a(b)?c(?(1)d|e){2}', 'text-0')", None, True),
        ("stdlib", None, None, True),
        ("stdlib", "backend.match('a(b)?c(?(1)d|e){2}', 'text-0')", None, True),
        ("stdlib", None, None, True),
        ("stdlib", "backend.fullmatch('a(b)?c(?(1)d|e){2}', 'text-0')", None, True),
        ("stdlib", None, None, True),
    ]


def test_assert_generated_text_matrix_matches_cpython_appends_labelled_first_helper_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regex_backend = ("stdlib", _GeneratedMatrixBackendContract("backend"))
    case = _generated_matrix_case_contract(r"a(b)?c(?(1)d|e){2}")

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        lambda *args, **kwargs: (
            _GeneratedMatrixPatternContract("observed-pattern"),
            _GeneratedMatrixPatternContract("expected-pattern"),
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        lambda observed, expected: (_ for _ in ()).throw(
            AssertionError("convenience drift")
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "search",
        lambda pattern, text: "expected-search-match",
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "match",
        lambda pattern, text: "expected-match-match",
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "fullmatch",
        lambda pattern, text: "expected-fullmatch-match",
    )

    with pytest.raises(AssertionError) as exc_info:
        fixture_parity_support.assert_generated_text_matrix_matches_cpython(
            regex_backend,
            case,
            candidate_texts=("text-0",),
            pattern_extractor=str_case_pattern,
            failure_prefix="generated helper drifted",
        )

    assert str(exc_info.value) == (
        "generated helper drifted:\n"
        "module.search('a(b)?c(?(1)d|e){2}', 'text-0'): convenience drift\n"
        "pattern.search('a(b)?c(?(1)d|e){2}', 'text-0'): convenience drift\n"
        "module.match('a(b)?c(?(1)d|e){2}', 'text-0'): convenience drift\n"
        "pattern.match('a(b)?c(?(1)d|e){2}', 'text-0'): convenience drift\n"
        "module.fullmatch('a(b)?c(?(1)d|e){2}', 'text-0'): convenience drift\n"
        "pattern.fullmatch('a(b)?c(?(1)d|e){2}', 'text-0'): convenience drift"
    )


def test_assert_generated_text_matrix_matches_cpython_truncates_failure_preview(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regex_backend = ("stdlib", _GeneratedMatrixBackendContract("backend"))
    case = _generated_matrix_case_contract(r"a(b)?c(?(1)d|e){2}")
    candidate_texts = tuple(f"text-{index}" for index in range(4))

    monkeypatch.setattr(
        fixture_parity_support,
        "compile_with_cpython_parity",
        lambda *args, **kwargs: (
            _GeneratedMatrixPatternContract("observed-pattern"),
            _GeneratedMatrixPatternContract("expected-pattern"),
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        lambda observed, expected: (_ for _ in ()).throw(
            AssertionError("preview drift")
        ),
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "search",
        lambda pattern, text: "expected-search-match",
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "match",
        lambda pattern, text: "expected-match-match",
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "fullmatch",
        lambda pattern, text: "expected-fullmatch-match",
    )

    with pytest.raises(AssertionError) as exc_info:
        fixture_parity_support.assert_generated_text_matrix_matches_cpython(
            regex_backend,
            case,
            candidate_texts=candidate_texts,
            pattern_extractor=str_case_pattern,
            failure_prefix="generated preview drifted",
        )

    assert str(exc_info.value) == (
        "generated preview drifted:\n"
        "module.search('a(b)?c(?(1)d|e){2}', 'text-0'): preview drift\n"
        "pattern.search('a(b)?c(?(1)d|e){2}', 'text-0'): preview drift\n"
        "module.match('a(b)?c(?(1)d|e){2}', 'text-0'): preview drift\n"
        "pattern.match('a(b)?c(?(1)d|e){2}', 'text-0'): preview drift\n"
        "module.fullmatch('a(b)?c(?(1)d|e){2}', 'text-0'): preview drift\n"
        "pattern.fullmatch('a(b)?c(?(1)d|e){2}', 'text-0'): preview drift\n"
        "module.search('a(b)?c(?(1)d|e){2}', 'text-1'): preview drift\n"
        "pattern.search('a(b)?c(?(1)d|e){2}', 'text-1'): preview drift\n"
        "module.match('a(b)?c(?(1)d|e){2}', 'text-1'): preview drift\n"
        "pattern.match('a(b)?c(?(1)d|e){2}', 'text-1'): preview drift\n"
        "module.fullmatch('a(b)?c(?(1)d|e){2}', 'text-1'): preview drift\n"
        "pattern.fullmatch('a(b)?c(?(1)d|e){2}', 'text-1'): preview drift\n"
        "module.search('a(b)?c(?(1)d|e){2}', 'text-2'): preview drift\n"
        "pattern.search('a(b)?c(?(1)d|e){2}', 'text-2'): preview drift\n"
        "module.match('a(b)?c(?(1)d|e){2}', 'text-2'): preview drift\n"
        "pattern.match('a(b)?c(?(1)d|e){2}', 'text-2'): preview drift\n"
        "module.fullmatch('a(b)?c(?(1)d|e){2}', 'text-2'): preview drift\n"
        "pattern.fullmatch('a(b)?c(?(1)d|e){2}', 'text-2'): preview drift\n"
        "module.search('a(b)?c(?(1)d|e){2}', 'text-3'): preview drift\n"
        "pattern.search('a(b)?c(?(1)d|e){2}', 'text-3'): preview drift\n"
        "... 4 more"
    )


@pytest.mark.parametrize(
    ("pattern_extractor", "case", "candidate_texts", "expected_pattern", "expected_flags"),
    (
        pytest.param(
            case_pattern,
            _generated_matrix_case_contract(rb"a((b|c)+)\2d", flags=1),
            (b"abbd",),
            rb"a((b|c)+)\2d",
            1,
            id="case-pattern-bytes",
        ),
        pytest.param(
            str_case_pattern,
            _generated_matrix_case_contract(r"a(b)?c(?(1)|(?:|))", flags=2),
            ("abc",),
            r"a(b)?c(?(1)|(?:|))",
            2,
            id="str-case-pattern-str",
        ),
    ),
)
def test_assert_generated_text_matrix_matches_cpython_accepts_current_pattern_extractors(
    monkeypatch: pytest.MonkeyPatch,
    pattern_extractor: Callable[[FixtureCase], str | bytes],
    case: FixtureCase,
    candidate_texts: tuple[str | bytes, ...],
    expected_pattern: str | bytes,
    expected_flags: int,
) -> None:
    regex_backend = ("stdlib", _GeneratedMatrixBackendContract("backend"))
    compile_calls: list[tuple[str | bytes, int]] = []

    def _compile(
        backend_name: str,
        backend: object,
        pattern: str | bytes,
        flags: int = 0,
        *,
        check_cache_identity: bool = True,
    ) -> tuple[object, object]:
        assert backend_name == "stdlib"
        assert backend is regex_backend[1]
        assert check_cache_identity is True
        compile_calls.append((pattern, flags))
        return (
            _GeneratedMatrixPatternContract("observed-pattern"),
            _GeneratedMatrixPatternContract("expected-pattern"),
        )

    monkeypatch.setattr(fixture_parity_support, "compile_with_cpython_parity", _compile)
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "search",
        lambda pattern, text: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "match",
        lambda pattern, text: None,
    )
    monkeypatch.setattr(
        fixture_parity_support.re,
        "fullmatch",
        lambda pattern, text: None,
    )

    fixture_parity_support.assert_generated_text_matrix_matches_cpython(
        regex_backend,
        case,
        candidate_texts=candidate_texts,
        pattern_extractor=pattern_extractor,
        failure_prefix="generated extractor drifted",
    )

    assert compile_calls == [(expected_pattern, expected_flags)]


@pytest.mark.parametrize(
    ("template", "use_compiled_pattern"),
    (
        pytest.param(b"<\\g<0>>", False, id="module-bytes-whole-match"),
        pytest.param(b"<\\\\>", True, id="pattern-bytes-escaped-backslash"),
        pytest.param(bytearray(b"<\\g<0>>"), False, id="module-bytes-bytearray"),
        pytest.param(memoryview(b"<\\\\>"), True, id="pattern-bytes-memoryview"),
    ),
)
def test_match_expand_bytes_templates_match_cpython(
    regex_backend: tuple[str, object],
    template: bytes | bytearray | memoryview,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _expand_match(
        backend_name,
        backend,
        BYTES_LITERAL_PATTERN,
        b"zzabczz",
        use_compiled_pattern=use_compiled_pattern,
    )

    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)

    expanded = observed.expand(template)
    expected_expanded = expected.expand(template)

    assert type(expanded) is type(expected_expanded)
    assert expanded == expected_expanded


@pytest.mark.parametrize(
    ("pattern", "text", "template", "use_compiled_pattern"),
    (
        pytest.param("(abc)", "abc", r"<\2>", False, id="str-invalid-numbered-reference"),
        pytest.param(
            r"(?P<word>abc)",
            "abc",
            r"<\g<missing>>",
            True,
            id="str-unknown-group-name",
        ),
        pytest.param(
            r"(?P<word>abc)",
            "abc",
            r"<\g<word",
            False,
            id="str-unterminated-group-name",
        ),
        pytest.param("(abc)", "abc", r"<\x>", True, id="str-bad-escape"),
        pytest.param(
            BYTES_LITERAL_PATTERN,
            b"abc",
            b"<\\1>",
            False,
            id="bytes-invalid-numbered-reference",
        ),
        pytest.param(
            BYTES_LITERAL_PATTERN,
            b"abc",
            b"<\\g<missing>>",
            True,
            id="bytes-unknown-group-name",
        ),
        pytest.param(
            BYTES_LITERAL_PATTERN,
            b"abc",
            b"<\\g<0",
            False,
            id="bytes-unterminated-group-name",
        ),
        pytest.param(
            BYTES_LITERAL_PATTERN,
            b"abc",
            bytearray(b"<\\1>"),
            False,
            id="bytes-invalid-numbered-reference-bytearray",
        ),
        pytest.param(
            BYTES_LITERAL_PATTERN,
            b"abc",
            memoryview(b"<\\g<missing>>"),
            True,
            id="bytes-unknown-group-name-memoryview",
        ),
        pytest.param(
            "(abc)",
            "abc",
            bytearray(b"<\\g<0>>"),
            False,
            id="str-bytearray-type-error",
        ),
        pytest.param(
            "(abc)",
            "abc",
            memoryview(b"<\\g<0>>"),
            True,
            id="str-memoryview-type-error",
        ),
    ),
)
def test_match_expand_error_paths_match_cpython(
    regex_backend: tuple[str, object],
    pattern: str | bytes,
    text: str | bytes,
    template: str | bytes | bytearray | memoryview,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _expand_match(
        backend_name,
        backend,
        pattern,
        text,
        use_compiled_pattern=use_compiled_pattern,
    )

    assert_match_parity(backend_name, observed, expected, check_regs=True)

    expected_error = _capture_expand_error(expected, template)

    with pytest.raises(type(expected_error)) as observed_error_info:
        observed.expand(template)

    observed_error = observed_error_info.value
    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args

    if isinstance(expected_error, re.error):
        assert observed_error.pattern == expected_error.pattern
        assert observed_error.pos == expected_error.pos


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-finditer"),
        pytest.param(True, id="pattern-finditer"),
    ),
)
def test_finditer_parity_helper_covers_match_metadata_and_iterator_exhaustion(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    pattern = "abc"
    text = "zabcabc"

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed_iter = observed_pattern.finditer(text)
        expected_iter = expected_pattern.finditer(text)
    else:
        observed_iter = backend.finditer(pattern, text)
        expected_iter = re.finditer(pattern, text)

    assert_finditer_parity(
        backend_name,
        observed_iter,
        expected_iter,
        check_regs=True,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-finditer"),
        pytest.param(True, id="pattern-finditer"),
    ),
)
def test_finditer_parity_helper_invokes_match_callback_for_each_match_in_order(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    pattern = "abc"
    text = "zabcabc"
    callback_pairs: list[tuple[tuple[int, int], tuple[int, int], str, str]] = []

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed_iter = observed_pattern.finditer(text)
        expected_iter = expected_pattern.finditer(text)
    else:
        observed_iter = backend.finditer(pattern, text)
        expected_iter = re.finditer(pattern, text)

    def record_match_pair(
        observed: object,
        expected: re.Match[str] | re.Match[bytes],
    ) -> None:
        callback_pairs.append(
            (
                observed.span(),
                expected.span(),
                observed.group(0),
                expected.group(0),
            )
        )

    assert_finditer_parity(
        backend_name,
        observed_iter,
        expected_iter,
        check_regs=True,
        match_callback=record_match_pair,
    )

    assert callback_pairs == [
        ((1, 4), (1, 4), "abc", "abc"),
        ((4, 7), (4, 7), "abc", "abc"),
    ]


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-finditer"),
        pytest.param(True, id="pattern-finditer"),
    ),
)
def test_finditer_parity_helper_covers_bytes_match_metadata_and_iterator_exhaustion(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    pattern = b"abc"
    text = b"zabcabc"

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed_iter = observed_pattern.finditer(text)
        expected_iter = expected_pattern.finditer(text)
    else:
        observed_iter = backend.finditer(pattern, text)
        expected_iter = re.finditer(pattern, text)

    assert_finditer_parity(
        backend_name,
        observed_iter,
        expected_iter,
        check_regs=True,
    )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-finditer"),
        pytest.param(True, id="pattern-finditer"),
    ),
)
def test_finditer_parity_helper_invokes_match_callback_for_each_bytes_match_in_order(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    pattern = b"abc"
    text = b"zabcabc"
    callback_pairs: list[tuple[tuple[int, int], tuple[int, int], bytes, bytes]] = []

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed_iter = observed_pattern.finditer(text)
        expected_iter = expected_pattern.finditer(text)
    else:
        observed_iter = backend.finditer(pattern, text)
        expected_iter = re.finditer(pattern, text)

    def record_match_pair(
        observed: object,
        expected: re.Match[str] | re.Match[bytes],
    ) -> None:
        callback_pairs.append(
            (
                observed.span(),
                expected.span(),
                observed.group(0),
                expected.group(0),
            )
        )

    assert_finditer_parity(
        backend_name,
        observed_iter,
        expected_iter,
        check_regs=True,
        match_callback=record_match_pair,
    )

    assert callback_pairs == [
        ((1, 4), (1, 4), b"abc", b"abc"),
        ((4, 7), (4, 7), b"abc", b"abc"),
    ]


def test_finditer_parity_helper_propagates_match_callback_failures() -> None:
    def fail_on_first_match(
        observed: object,
        expected: re.Match[str] | re.Match[bytes],
    ) -> None:
        raise AssertionError(
            f"callback drift for {observed.span()} vs {expected.span()}"
        )

    with pytest.raises(
        AssertionError,
        match=re.escape("callback drift for (0, 3) vs (0, 3)"),
    ):
        assert_finditer_parity(
            "stub-backend",
            re.finditer("abc", "abc"),
            re.finditer("abc", "abc"),
            match_callback=fail_on_first_match,
        )


def test_finditer_parity_helper_skips_match_callback_for_shared_empty_iterators() -> None:
    callback_calls: list[tuple[object, object]] = []

    def record_match_pair(observed: object, expected: object) -> None:
        callback_calls.append((observed, expected))

    assert_finditer_parity(
        "stub-backend",
        re.finditer("abc", "zzz"),
        re.finditer("abc", "zzz"),
        match_callback=record_match_pair,
    )

    assert callback_calls == []


def test_finditer_parity_helper_rejects_iterator_that_resumes_after_exhaustion() -> None:
    class _ResumingIterator:
        def __init__(self, values: tuple[object, ...]) -> None:
            self._values = values
            self._index = 0
            self._stopped_once = False
            self._resumed = False

        def __iter__(self) -> "_ResumingIterator":
            return self

        def __next__(self) -> object:
            if self._index < len(self._values):
                value = self._values[self._index]
                self._index += 1
                return value
            if not self._stopped_once:
                self._stopped_once = True
                raise StopIteration
            if not self._resumed:
                self._resumed = True
                return self._values[-1]
            raise StopIteration

    with pytest.raises(AssertionError):
        assert_finditer_parity(
            "stub-backend",
            _ResumingIterator(tuple(re.finditer("abc", "abc"))),
            iter(()),
        )


def test_finditer_parity_helper_rejects_exhausted_non_self_iterables() -> None:
    class _AlreadyExhaustedNonSelfIterator:
        def __iter__(self) -> object:
            return iter(())

        def __next__(self) -> object:
            raise StopIteration

    with pytest.raises(
        AssertionError,
        match="finditer result must be its own iterator",
    ):
        assert_finditer_parity(
            "stub-backend",
            _AlreadyExhaustedNonSelfIterator(),
            iter(()),
        )


def test_finditer_parity_helper_rejects_non_self_cpython_iterators() -> None:
    class _AlreadyExhaustedNonSelfIterator:
        def __iter__(self) -> object:
            return iter(())

        def __next__(self) -> object:
            raise StopIteration

    with pytest.raises(
        AssertionError,
        match="CPython finditer result must be its own iterator",
    ):
        assert_finditer_parity(
            "stub-backend",
            iter(()),
            _AlreadyExhaustedNonSelfIterator(),
        )


def test_finditer_parity_helper_rejects_match_count_drift() -> None:
    with pytest.raises(
        AssertionError,
        match="stub-backend finditer yielded a different number of matches than CPython",
    ):
        assert_finditer_parity(
            "stub-backend",
            iter(()),
            re.finditer("abc", "abc"),
        )


def test_finditer_parity_helper_rejects_extra_match_after_shared_prefix() -> None:
    matches = tuple(re.finditer("abc", "abcabc"))

    with pytest.raises(
        AssertionError,
        match="stub-backend finditer yielded a different number of matches than CPython",
    ):
        assert_finditer_parity(
            "stub-backend",
            iter(matches),
            iter(matches[:1]),
        )


def test_placeholder_message_contains_accepts_substring_match() -> None:
    fixture_parity_support.assert_placeholder_message_contains(
        NotImplementedError("native helper placeholder search"),
        "placeholder search",
    )


def test_placeholder_message_contains_rejects_missing_substring() -> None:
    with pytest.raises(AssertionError):
        fixture_parity_support.assert_placeholder_message_contains(
            NotImplementedError("native helper placeholder search"),
            "placeholder compile",
        )


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-fullmatch"),
        pytest.param(True, id="pattern-fullmatch"),
    ),
)
def test_match_result_parity_accepts_shared_no_match_paths(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _optional_named_group_match(
        backend_name,
        backend,
        "zz",
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "use_compiled_pattern",
    (
        pytest.param(False, id="module-search"),
        pytest.param(True, id="pattern-search"),
    ),
)
def test_match_result_parity_accepts_shared_bytes_no_match_paths(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _bytes_literal_search_match(
        backend_name,
        backend,
        b"zzz",
        use_compiled_pattern=use_compiled_pattern,
    )

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)


def test_match_result_parity_rejects_unexpected_match_when_cpython_has_none() -> None:
    with pytest.raises(AssertionError):
        assert_match_result_parity(
            "stub-backend",
            re.search("abc", "abc"),
            None,
        )


def test_match_result_parity_rejects_missing_match_when_cpython_matches() -> None:
    expected = re.search("abc", "abc")

    assert expected is not None

    with pytest.raises(AssertionError):
        assert_match_result_parity(
            "stub-backend",
            None,
            expected,
        )
