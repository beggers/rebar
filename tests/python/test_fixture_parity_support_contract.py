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
    declared_string_constants_by_suffix,
    ordered_published_subset_filenames,
)
from tests.conftest import duplicate_items
import tests.python.fixture_parity_support as fixture_parity_support
from tests.python.fixture_parity_support import (
    FixtureBundle,
    assert_bounded_pattern_case_match_parity,
    assert_bounded_pattern_case_no_match_parity,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_finditer_parity,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_module_search_case_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    assert_pattern_fullmatch_case_parity,
    assert_value_parity,
    assert_valid_match_group_access_parity,
    build_fixture_bundle,
    build_selected_fixture_bundle,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    invoke_bounded_pattern_case,
    str_case_pattern,
    workflow_result_with_cpython_parity,
)
OPTIONAL_NAMED_GROUP_PATTERN = r"a(?P<word>b)?d"
BYTES_LITERAL_PATTERN = b"abc"


class _NonCachingStdlibBackend:
    @staticmethod
    def compile(
        pattern: str | bytes,
        flags: int = 0,
    ) -> re.Pattern[str] | re.Pattern[bytes]:
        re.purge()
        return re.compile(pattern, flags)


def _declared_nondefault_correctness_fixture_selectors() -> tuple[str, ...]:
    return tuple(
        sorted(
            selector
            for selector in declared_string_constants_by_suffix(
                correctness,
                name_suffix="_FIXTURE_SELECTOR",
            ).values()
            if selector != PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
        )
    )


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


CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS = (
    pytest.param(
        PARSER_PARITY_FIXTURE_SELECTOR,
        (
            "parser_matrix.py",
            "conditional_group_exists_assertion_diagnostics.py",
        ),
        id=PARSER_PARITY_FIXTURE_SELECTOR,
    ),
    pytest.param(
        PUBLIC_SURFACE_FIXTURE_SELECTOR,
        (
            "public_api_surface.py",
            "exported_symbol_surface.py",
            "pattern_object_surface.py",
        ),
        id=PUBLIC_SURFACE_FIXTURE_SELECTOR,
    ),
)
def _load_published_fixture_bundle(
    fixture_path: pathlib.Path,
    *,
    pattern_extractor: Callable[[FixtureCase], str | bytes] = case_pattern,
) -> FixtureBundle:
    (bundle,) = fixture_parity_support.load_published_fixture_bundles(
        (fixture_path,),
        pattern_extractor=pattern_extractor,
    )
    return bundle


def _load_bundle_loader_contract_str_bundle(tmp_path: pathlib.Path) -> FixtureBundle:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    return _load_published_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )


def _load_bundle_loader_contract_mixed_bundle(tmp_path: pathlib.Path) -> FixtureBundle:
    _, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    return _load_published_fixture_bundle(
        mixed_path,
        pattern_extractor=case_pattern,
    )


def test_build_fixture_bundle_derives_patterns_and_operation_counts_from_cases(
    tmp_path: pathlib.Path,
) -> None:
    _, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    manifest = load_fixture_manifest(mixed_path)
    bundle_cases = (
        manifest.cases[3],
        manifest.cases[1],
        manifest.cases[0],
    )
    expected_case_ids = frozenset(case.case_id for case in bundle_cases)

    bundle = build_fixture_bundle(
        manifest,
        bundle_cases,
        pattern_extractor=case_pattern,
        expected_case_ids=expected_case_ids,
        expected_text_models=frozenset({"bytes", "str"}),
    )

    assert bundle.manifest is manifest
    assert bundle.cases == bundle_cases
    assert bundle.expected_patterns == frozenset({r"a(bc|de){1,}d", rb"a(bc|de){1,}d"})
    assert bundle.expected_operation_helper_counts == Counter(
        {
            ("pattern_call", "fullmatch"): 1,
            ("module_call", "search"): 1,
            ("compile", None): 1,
        }
    )
    assert bundle.expected_case_ids == expected_case_ids
    assert bundle.expected_text_models == frozenset({"bytes", "str"})
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=mixed_path,
        expected_ordered_case_ids=tuple(case.case_id for case in bundle_cases),
    )


def test_build_fixture_bundle_requires_pattern_extractor_without_explicit_patterns(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    manifest = load_fixture_manifest(str_path)

    with pytest.raises(
        ValueError,
        match=re.escape(
            "pattern_extractor is required when expected_patterns is not provided"
        ),
    ):
        build_fixture_bundle(
            manifest,
            tuple(manifest.cases[:1]),
        )


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
    _declared_nondefault_correctness_fixture_selectors(),
)
def test_shared_correctness_fixture_selectors_resolve_published_paths(
    selector: str,
) -> None:
    published_full_suite_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    registry_filenames = correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector]
    resolved_paths = select_correctness_fixture_paths(selector)
    expected_ordered_subset = tuple(
        path
        for path in published_full_suite_paths
        if path.name in set(registry_filenames)
    )

    assert resolved_paths
    assert len(registry_filenames) == len(set(registry_filenames))
    assert len(resolved_paths) == len(set(resolved_paths))
    assert resolved_paths == tuple(
        CORRECTNESS_FIXTURES_ROOT / filename for filename in registry_filenames
    )
    assert expected_ordered_subset
    assert len(expected_ordered_subset) == len(resolved_paths)
    assert resolved_paths == expected_ordered_subset

    for path in resolved_paths:
        assert path.is_relative_to(CORRECTNESS_FIXTURES_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"
        assert path in published_full_suite_paths


@pytest.mark.parametrize(
    ("selector", "expected_filenames"),
    CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS,
)
def test_canonical_published_subset_selectors_keep_explicit_membership_contract(
    selector: str,
    expected_filenames: tuple[str, ...],
) -> None:
    published_full_suite_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    published_ordered_subset = tuple(
        path.name
        for path in published_full_suite_paths
        if path.name in set(expected_filenames)
    )

    assert published_ordered_subset == expected_filenames
    assert correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector] == (
        expected_filenames
    )
    assert tuple(path.name for path in select_correctness_fixture_paths(selector)) == (
        expected_filenames
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
    declared_selectors = declared_string_constants_by_suffix(
        correctness,
        name_suffix="_FIXTURE_SELECTOR",
    )

    assert declared_selectors
    assert len(declared_selectors) == len(set(declared_selectors.values()))
    assert set(declared_selectors.values()) == set(
        correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR
    )


def test_declared_nondefault_correctness_fixture_selectors_are_parametrized_once() -> None:
    declared_nondefault_selectors = set(
        declared_string_constants_by_suffix(
            correctness,
            name_suffix="_FIXTURE_SELECTOR",
        ).values()
    )
    declared_nondefault_selectors.remove(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)
    expected_selectors = _declared_nondefault_correctness_fixture_selectors()

    assert PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR not in expected_selectors
    assert len(expected_selectors) == len(set(expected_selectors))
    assert set(expected_selectors) == declared_nondefault_selectors


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
    manifests = published_fixture_manifests()
    cases = [case for manifest in manifests for case in manifest.cases]

    assert published_fixture_manifests() is manifests
    assert tuple(manifest.path for manifest in manifests) == DEFAULT_FIXTURE_PATHS
    assert tuple(manifest.path.name for manifest in manifests) == tuple(
        path.name for path in DEFAULT_FIXTURE_PATHS
    )
    assert duplicate_items(Counter(manifest.manifest_id for manifest in manifests)) == []
    assert duplicate_items(Counter(manifest.suite_id for manifest in manifests)) == []
    assert duplicate_items(Counter(case.case_id for case in cases)) == []

    cases_by_manifest = Counter(case.manifest_id for case in cases)
    manifest_ids = {manifest.manifest_id for manifest in manifests}

    for manifest in manifests:
        assert cases_by_manifest[manifest.manifest_id] > 0

    for case in cases:
        assert case.manifest_id in manifest_ids


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

    fixture_parity_support._assert_optional_match_case_parity(
        "rebar",
        object(),
        object(),
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

    fixture_parity_support._assert_optional_match_case_parity(
        "stub-backend",
        None,
        None,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )

    assert helper_calls == []


def test_evaluate_fixture_case_optional_match_keeps_raw_module_calls_on_module_helper_surface(
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

    backend_name, observed, expected = fixture_parity_support._evaluate_fixture_case_optional_match(
        ("stub-backend", _RecordingBackend()),
        SYNTHETIC_MODULE_PATTERN_CASE,
        expected_helper="search",
        compile_pattern=False,
    )

    expected_args = tuple(SYNTHETIC_MODULE_PATTERN_CASE.module_call_args())
    assert backend_name == "stub-backend"
    assert observed_calls == [(expected_args, {})]
    assert expected_calls == [(expected_args, {})]
    assert_match_result_parity(
        "stub-backend",
        observed,
        expected,
        check_regs=True,
    )


def test_evaluate_fixture_case_optional_match_routes_compiled_module_calls_through_compiled_pattern_argument(
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
    backend_name, observed, expected = fixture_parity_support._evaluate_fixture_case_optional_match(
        ("stub-backend", backend),
        SYNTHETIC_COMPILED_MODULE_PATTERN_CASE,
        expected_helper="search",
        compile_pattern=False,
    )

    assert backend_name == "stub-backend"
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
    assert_match_result_parity(
        "stub-backend",
        observed,
        expected,
        check_regs=True,
    )


def test_evaluate_fixture_case_optional_match_routes_pattern_calls_through_compiled_patterns(
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
    backend_name, observed, expected = fixture_parity_support._evaluate_fixture_case_optional_match(
        ("stub-backend", backend),
        SYNTHETIC_FULLMATCH_PATTERN_CASE,
        expected_helper="fullmatch",
        compile_pattern=True,
    )

    assert backend_name == "stub-backend"
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
    assert_match_result_parity(
        "stub-backend",
        observed,
        expected,
        check_regs=True,
    )


def test_evaluate_fixture_case_optional_match_rejects_helper_drift() -> None:
    with pytest.raises(AssertionError):
        fixture_parity_support._evaluate_fixture_case_optional_match(
            ("stub-backend", object()),
            SYNTHETIC_FULLMATCH_PATTERN_CASE,
            expected_helper="search",
            compile_pattern=True,
        )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_MODULE_PATTERN_CASE, id="str-match"),
        pytest.param(SYNTHETIC_MODULE_BYTES_SEARCH_CASE, id="bytes-match"),
    ),
)
def test_module_search_case_parity_helper_accepts_representative_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(
        regex_backend,
        case,
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
def test_module_search_case_parity_helper_accepts_compiled_pattern_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(
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
def test_module_search_case_parity_helper_accepts_shared_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(
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
def test_module_search_case_parity_helper_accepts_compiled_pattern_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_module_search_case_parity(
        regex_backend,
        case,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


def test_module_search_case_parity_helper_rejects_non_search_cases(
    regex_backend: tuple[str, object],
) -> None:
    with pytest.raises(AssertionError):
        assert_module_search_case_parity(
            regex_backend,
            replace(SYNTHETIC_MODULE_PATTERN_CASE, helper="match"),
        )


@pytest.mark.parametrize(
    "case",
    (
        pytest.param(SYNTHETIC_FULLMATCH_PATTERN_CASE, id="str-match"),
        pytest.param(SYNTHETIC_FULLMATCH_BYTES_PATTERN_CASE, id="bytes-match"),
    ),
)
def test_pattern_fullmatch_case_parity_helper_accepts_representative_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_pattern_fullmatch_case_parity(
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
def test_pattern_fullmatch_case_parity_helper_accepts_shared_no_match_cases(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    assert_pattern_fullmatch_case_parity(
        regex_backend,
        case,
        check_regs=True,
        check_convenience_api=True,
        check_group_access=True,
    )


def test_pattern_fullmatch_case_parity_helper_rejects_non_fullmatch_cases(
    regex_backend: tuple[str, object],
) -> None:
    with pytest.raises(AssertionError):
        assert_pattern_fullmatch_case_parity(
            regex_backend,
            replace(SYNTHETIC_FULLMATCH_PATTERN_CASE, helper="search"),
        )


def test_evaluate_bounded_pattern_case_compiles_then_dispatches_observed_and_expected_patterns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compile_calls: list[tuple[object, ...]] = []
    dispatched_patterns: list[tuple[object, object]] = []
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

    backend = object()
    assert fixture_parity_support._evaluate_bounded_pattern_case(
        ("stub-backend", backend),
        case,
    ) == ("stub-backend", observed_match, expected_match)
    assert compile_calls == [("stub-backend", backend, "abc", 0, True)]
    assert dispatched_patterns == [
        (observed_pattern, case),
        (expected_pattern, case),
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
def test_bounded_pattern_case_no_match_parity_helper_accepts_representative_cases(
    regex_backend: tuple[str, object],
    case: SimpleNamespace,
) -> None:
    assert_bounded_pattern_case_no_match_parity(
        regex_backend,
        case,
        check_regs=True,
    )


def test_whole_manifest_bundle_contract_supports_full_manifest_counts_without_case_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    str_bundle, mixed_bundle = fixture_parity_support.load_published_fixture_bundles(
        (str_path, mixed_path)
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


def test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(
    tmp_path: pathlib.Path,
) -> None:
    field_names = {field.name for field in fields(FixtureBundle)}
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = _load_published_fixture_bundle(
        str_path,
        pattern_extractor=str_case_pattern,
    )

    assert "expected_manifest_id" not in field_names
    assert bundle.expected_manifest_id == BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID
    assert bundle.expected_manifest_id == bundle.manifest.manifest_id


def test_load_published_fixture_bundles_derives_full_manifest_contracts_in_input_order(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles = fixture_parity_support.load_published_fixture_bundles(
        (mixed_path, str_path)
    )
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


def test_load_published_fixture_bundles_custom_pattern_extractor_only_changes_expected_patterns(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)

    default_bundles = fixture_parity_support.load_published_fixture_bundles(
        (mixed_path, str_path)
    )

    def _case_id_pattern(case: FixtureCase) -> str:
        return case.case_id

    custom_bundles = fixture_parity_support.load_published_fixture_bundles(
        (mixed_path, str_path),
        pattern_extractor=_case_id_pattern,
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


def test_published_fixture_bundle_by_manifest_id_returns_requested_bundle(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles = fixture_parity_support.load_published_fixture_bundles(
        (str_path, mixed_path)
    )
    mixed_bundle = fixture_parity_support.published_fixture_bundle_by_manifest_id(
        bundles,
        BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
    )
    str_bundle = fixture_parity_support.published_fixture_bundle_by_manifest_id(
        bundles,
        BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
    )

    assert mixed_bundle is bundles[1]
    assert str_bundle is bundles[0]


def test_published_fixture_bundle_by_manifest_id_map_returns_requested_bundles(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles = fixture_parity_support.load_published_fixture_bundles(
        (str_path, mixed_path)
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


def test_published_fixture_bundle_by_manifest_id_rejects_missing_manifest_id(
    tmp_path: pathlib.Path,
) -> None:
    str_path, mixed_path = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundles = fixture_parity_support.load_published_fixture_bundles(
        (str_path, mixed_path)
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundles do not contain manifest_id 'missing-manifest-id'"
        ),
    ):
        fixture_parity_support.published_fixture_bundle_by_manifest_id(
            bundles,
            "missing-manifest-id",
        )


def test_published_fixture_bundle_by_manifest_id_rejects_duplicate_manifest_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((str_path,))

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundles contain duplicate manifest_id "
            f"'{BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID}'"
        ),
    ):
        fixture_parity_support.published_fixture_bundle_by_manifest_id(
            (bundle, bundle),
            BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
        )


def test_published_fixture_bundle_by_manifest_id_map_rejects_duplicate_manifest_ids(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((str_path,))

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundles contain duplicate manifest_id "
            f"'{BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID}'"
        ),
    ):
        fixture_parity_support.published_fixture_bundles_by_manifest_id(
            (bundle, bundle)
        )


def test_assert_direct_bytes_follow_on_bundle_routing_accepts_mixed_manifest_buckets(
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))
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
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))
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
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))
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
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))
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
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))

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
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))
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
    follow_on_bundle, preserved_bundle = fixture_parity_support.load_published_fixture_bundles(
        (follow_on_fixture_path, preserved_fixture_path)
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


def test_direct_test_case_id_buckets_for_follow_on_bundles_keeps_shared_and_bytes_rows_separate(
) -> None:
    follow_on_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    preserved_fixture_path = (
        CORRECTNESS_FIXTURES_ROOT
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    follow_on_bundle, preserved_bundle = fixture_parity_support.load_published_fixture_bundles(
        (follow_on_fixture_path, preserved_fixture_path)
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


def test_published_bytes_texts_by_pattern_separates_search_and_fullmatch_rows(
) -> None:
    fixture_path = (
        CORRECTNESS_FIXTURES_ROOT / "quantified_alternation_open_ended_workflows.py"
    )
    (bundle,) = fixture_parity_support.load_published_fixture_bundles((fixture_path,))
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
    str_bundle, mixed_bundle = fixture_parity_support.load_published_fixture_bundles(
        (str_path, mixed_path)
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
    assert bundle.expected_text_models is None
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
        expected_text_models=frozenset({"bytes", "str"}),
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


def test_load_published_fixture_bundles_full_manifest_sets_str_text_model_expectation(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    bundle = _load_published_fixture_bundle(
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
    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)

    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=(published_case_ids[0], published_case_ids[2]),
        expected_uncovered_case_ids=(published_case_ids[1],),
    )


def test_assert_fixture_bundle_tracks_published_case_frontier_accepts_selected_and_uncovered_rows_for_mixed_manifest(
    tmp_path: pathlib.Path,
) -> None:
    bundle = _load_bundle_loader_contract_mixed_bundle(tmp_path)
    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)

    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=(published_case_ids[1], published_case_ids[3]),
        expected_uncovered_case_ids=(published_case_ids[0], published_case_ids[2]),
    )


@pytest.mark.parametrize("duplicate_source", ("selected", "uncovered"))
def test_assert_fixture_bundle_tracks_published_case_frontier_rejects_duplicate_case_ids(
    tmp_path: pathlib.Path,
    duplicate_source: str,
) -> None:
    bundle = _load_bundle_loader_contract_str_bundle(tmp_path)
    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)

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
    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)
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
    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)
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
    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)
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


def test_record_generated_match_failure_skips_match_specific_checks_for_no_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failures: list[str] = []
    calls: list[tuple[str, object]] = []

    def _record_match_result(
        backend_name: str,
        observed: object,
        expected: object,
        *,
        check_regs: bool = False,
    ) -> None:
        calls.append(
            ("result", backend_name, observed, expected, check_regs)
        )

    def _unexpected_follow_on(*args: object, **kwargs: object) -> None:
        raise AssertionError("unexpected follow-on helper call")

    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        _record_match_result,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        _unexpected_follow_on,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        _unexpected_follow_on,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        _unexpected_follow_on,
    )

    fixture_parity_support.record_generated_match_failure(
        failures,
        label="generated-no-match",
        backend_name="stdlib",
        observed=None,
        expected=None,
    )

    assert failures == []
    assert calls == [("result", "stdlib", None, None, True)]


def test_record_generated_match_failure_runs_follow_on_checks_for_expected_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failures: list[str] = []
    calls: list[str] = []
    observed = object()
    expected = object()

    def _record_match_result(
        backend_name: str,
        match_observed: object,
        match_expected: object,
        *,
        check_regs: bool = False,
    ) -> None:
        calls.append("result")
        assert backend_name == "stdlib"
        assert match_observed is observed
        assert match_expected is expected
        assert check_regs is True

    def _record_convenience(
        match_observed: object,
        match_expected: object,
    ) -> None:
        calls.append("convenience")
        assert match_observed is observed
        assert match_expected is expected

    def _record_valid_group_access(
        match_observed: object,
        match_expected: object,
    ) -> None:
        calls.append("valid-group-access")
        assert match_observed is observed
        assert match_expected is expected

    def _record_invalid_group_access(
        match_observed: object,
        match_expected: object,
    ) -> None:
        calls.append("invalid-group-access")
        assert match_observed is observed
        assert match_expected is expected

    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        _record_match_result,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        _record_convenience,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        _record_valid_group_access,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        _record_invalid_group_access,
    )

    fixture_parity_support.record_generated_match_failure(
        failures,
        label="generated-match",
        backend_name="stdlib",
        observed=observed,
        expected=expected,
    )

    assert failures == []
    assert calls == [
        "result",
        "convenience",
        "valid-group-access",
        "invalid-group-access",
    ]


@pytest.mark.parametrize(
    ("failing_stage", "expected_calls"),
    (
        pytest.param("result", ("result",), id="match-result"),
        pytest.param(
            "valid-group-access",
            ("result", "convenience", "valid-group-access"),
            id="valid-group-access",
        ),
    ),
)
def test_record_generated_match_failure_appends_labelled_first_helper_failure(
    monkeypatch: pytest.MonkeyPatch,
    failing_stage: str,
    expected_calls: tuple[str, ...],
) -> None:
    failures: list[str] = []
    calls: list[str] = []
    observed = object()
    expected = object()
    failure_message = f"{failing_stage} drift"

    def _maybe_raise(stage: str) -> None:
        calls.append(stage)
        if stage == failing_stage:
            raise AssertionError(failure_message)

    def _record_match_result(
        backend_name: str,
        match_observed: object,
        match_expected: object,
        *,
        check_regs: bool = False,
    ) -> None:
        assert backend_name == "stdlib"
        assert match_observed is observed
        assert match_expected is expected
        assert check_regs is True
        _maybe_raise("result")

    def _record_convenience(
        match_observed: object,
        match_expected: object,
    ) -> None:
        assert match_observed is observed
        assert match_expected is expected
        _maybe_raise("convenience")

    def _record_valid_group_access(
        match_observed: object,
        match_expected: object,
    ) -> None:
        assert match_observed is observed
        assert match_expected is expected
        _maybe_raise("valid-group-access")

    def _record_invalid_group_access(
        match_observed: object,
        match_expected: object,
    ) -> None:
        assert match_observed is observed
        assert match_expected is expected
        _maybe_raise("invalid-group-access")

    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_result_parity",
        _record_match_result,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_match_convenience_api_parity",
        _record_convenience,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_valid_match_group_access_parity",
        _record_valid_group_access,
    )
    monkeypatch.setattr(
        fixture_parity_support,
        "assert_invalid_match_group_access_parity",
        _record_invalid_group_access,
    )

    fixture_parity_support.record_generated_match_failure(
        failures,
        label="generated-case",
        backend_name="stdlib",
        observed=observed,
        expected=expected,
    )

    assert failures == [f"generated-case: {failure_message}"]
    assert calls == list(expected_calls)


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
