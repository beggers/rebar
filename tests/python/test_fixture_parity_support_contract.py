from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields, replace
import pathlib
import re
import textwrap
from types import SimpleNamespace

import pytest

import rebar
from rebar_harness import correctness
from rebar_harness.correctness import (
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    BOUNDED_WILDCARD_FIXTURE_SELECTOR,
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    COUNTED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    CORRECTNESS_FIXTURES_ROOT,
    DEFAULT_FIXTURE_PATHS,
    FixtureCase,
    GROUPED_CAPTURE_FIXTURE_SELECTOR,
    LITERAL_FLAG_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR,
    SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
    WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    load_fixture_manifest,
    load_fixture_manifests,
    published_fixture_manifests,
    select_correctness_fixture_paths,
)
import tests.python.fixture_parity_support as fixture_parity_support
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    RecordingNativeBoundary,
    assert_bounded_pattern_case_match_parity,
    assert_bounded_pattern_case_no_match_parity,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_finditer_parity,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_module_search_case_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    assert_pattern_fullmatch_case_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    invoke_bounded_pattern_case,
    load_fixture_bundles,
    str_case_pattern,
    workflow_result_with_cpython_parity,
)
OPTIONAL_NAMED_GROUP_PATTERN = r"a(?P<word>b)?d"
BYTES_LITERAL_PATTERN = b"abc"
SELECTOR_EXPECTATION_TABLE = (
    (
        COUNTED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
        (
            "exact_repeat_quantified_group_workflows.py",
            "ranged_repeat_quantified_group_workflows.py",
        ),
        "counted-repeat",
    ),
    (
        QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR,
        (
            "exact_repeat_quantified_group_alternation_workflows.py",
            "literal_alternation_workflows.py",
            "quantified_alternation_backtracking_heavy_workflows.py",
            "quantified_alternation_broader_range_workflows.py",
            "quantified_alternation_conditional_workflows.py",
            "quantified_alternation_nested_branch_workflows.py",
            "quantified_alternation_open_ended_workflows.py",
            "quantified_alternation_workflows.py",
            "quantified_nested_group_alternation_workflows.py",
        ),
        "quantified-alternation",
    ),
    (
        BOUNDED_WILDCARD_FIXTURE_SELECTOR,
        (
            "collection_replacement_workflows.py",
            "literal_flag_workflows.py",
        ),
        "bounded-wildcard",
    ),
    (
        SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
        (
            "named_backreference_workflows.py",
            "numbered_backreference_workflows.py",
        ),
        "simple-backreference",
    ),
    (
        GROUPED_CAPTURE_FIXTURE_SELECTOR,
        (
            "grouped_alternation_workflows.py",
            "grouped_match_workflows.py",
            "grouped_segment_workflows.py",
            "named_group_workflows.py",
            "nested_group_alternation_workflows.py",
            "nested_group_workflows.py",
            "optional_group_alternation_workflows.py",
            "optional_group_workflows.py",
        ),
        "grouped-capture",
    ),
    (
        WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
        (
            "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
            "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
            "broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
            "broader_range_wider_ranged_repeat_quantified_group_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
            "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
            "wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
            "wider_ranged_repeat_quantified_group_workflows.py",
        ),
        "wider-ranged-repeat",
    ),
    (
        BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
        (
            "branch_local_backreference_workflows.py",
            "conditional_group_exists_branch_local_backreference_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py",
            "nested_group_alternation_branch_local_backreference_workflows.py",
            "optional_group_alternation_branch_local_backreference_workflows.py",
            "quantified_alternation_branch_local_backreference_workflows.py",
            "quantified_branch_local_backreference_workflows.py",
            "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
        ),
        "branch-local-backreference",
    ),
    (
        LITERAL_FLAG_FIXTURE_SELECTOR,
        ("literal_flag_workflows.py",),
        "literal-flag",
    ),
    (
        CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
        (
            "conditional_group_exists_callable_replacement_workflows.py",
            "grouped_alternation_callable_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_callable_replacement_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py",
            "nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "nested_group_alternation_callable_replacement_workflows.py",
            "nested_group_callable_replacement_workflows.py",
            "nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "quantified_nested_group_alternation_callable_replacement_workflows.py",
            "quantified_nested_group_callable_replacement_workflows.py",
        ),
        "callable-replacement",
    ),
    (
        OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
        (
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
            "nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
        ),
        "open-ended-replacement-template",
    ),
    (
        OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
        (
            "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
            "broader_range_open_ended_quantified_group_alternation_conditional_workflows.py",
            "broader_range_open_ended_quantified_group_alternation_workflows.py",
            "nested_open_ended_quantified_group_alternation_workflows.py",
            "open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
            "open_ended_quantified_group_alternation_conditional_workflows.py",
            "open_ended_quantified_group_alternation_workflows.py",
        ),
        "open-ended-quantified-group",
    ),
    (
        CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
        (
            "conditional_group_exists_alternation_replacement_workflows.py",
            "conditional_group_exists_empty_else_replacement_workflows.py",
            "conditional_group_exists_empty_yes_else_replacement_workflows.py",
            "conditional_group_exists_fully_empty_replacement_workflows.py",
            "conditional_group_exists_nested_replacement_workflows.py",
            "conditional_group_exists_no_else_replacement_workflows.py",
            "conditional_group_exists_quantified_alternation_replacement_workflows.py",
            "conditional_group_exists_quantified_replacement_workflows.py",
            "conditional_group_exists_replacement_template_workflows.py",
            "conditional_group_exists_replacement_workflows.py",
        ),
        "conditional-replacement",
    ),
)
SELECTOR_EXPECTATIONS = tuple(
    pytest.param(selector, expected_filenames, id=selector_id)
    for selector, expected_filenames, selector_id in SELECTOR_EXPECTATION_TABLE
)


def _declared_correctness_fixture_selectors() -> dict[str, str]:
    return {
        name: value
        for name, value in vars(correctness).items()
        if name.endswith("_FIXTURE_SELECTOR") and isinstance(value, str)
    }


def _duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


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


def _bundle_loader_contract_str_spec() -> FixtureBundleSpec:
    return FixtureBundleSpec(
        BUNDLE_LOADER_CONTRACT_STR_FILENAME,
        expected_manifest_id=BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID,
        expected_case_ids=frozenset(
            {
                "bundle-loader-contract-compile-str",
                "bundle-loader-contract-module-search-str",
                "bundle-loader-contract-pattern-search-str",
            }
        ),
        expected_patterns=frozenset({r"(?P<word>ab)(?P=word)"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    )


def _bundle_loader_contract_mixed_spec() -> FixtureBundleSpec:
    return FixtureBundleSpec(
        BUNDLE_LOADER_CONTRACT_MIXED_FILENAME,
        expected_manifest_id=BUNDLE_LOADER_CONTRACT_MIXED_MANIFEST_ID,
        expected_patterns=frozenset({r"a(bc|de){1,}d", rb"a(bc|de){1,}d"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 1,
                ("pattern_call", "fullmatch"): 1,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    )


def _load_fixture_bundles_from_root(
    root: pathlib.Path,
    specs: tuple[FixtureBundleSpec, ...],
) -> tuple[FixtureBundle, ...]:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(fixture_parity_support, "CORRECTNESS_FIXTURES_ROOT", root)
        return load_fixture_bundles(specs)


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


class _EchoRecordingNativeBoundary(RecordingNativeBoundary):
    def compile_result(self, pattern: str | bytes, flags: int) -> tuple[str, str | bytes, int]:
        return ("compiled", pattern, flags)

    def literal_match_result(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, str, str | bytes, int, int | None]:
        return ("matched", mode, string, pos, endpos)

    def literal_split_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        maxsplit: int,
    ) -> tuple[str, list[str] | list[bytes]]:
        return ("supported", [string])

    def literal_findall_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes]]:
        return ("supported", [string])

    def literal_finditer_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, list[tuple[int, int]]]:
        return ("supported", pos, len(string) if endpos is None else endpos, [(pos, pos + 1)])

    def literal_subn_result(
        self,
        pattern: str | bytes,
        flags: int,
        repl: str | bytes,
        string: str | bytes,
        count: int,
    ) -> tuple[str, str | bytes, int]:
        return ("supported", repl, count)

    def escape_result(self, pattern: str | bytes) -> str | bytes:
        return pattern


def test_recording_native_boundary_dispatch_helpers_record_calls_and_results() -> None:
    boundary = _EchoRecordingNativeBoundary()

    assert boundary.boundary_compile("abc", 4) == ("compiled", "abc", 4)
    assert boundary.boundary_literal_match("abc", 4, "search", "zabc", 1, None) == (
        "matched",
        "search",
        "zabc",
        1,
        None,
    )
    assert boundary.boundary_literal_split(b"abc", 2, b"zabc", 1) == (
        "supported",
        [b"zabc"],
    )
    assert boundary.boundary_literal_findall("abc", 0, "zabc", 0, 4) == (
        "supported",
        ["zabc"],
    )
    assert boundary.boundary_literal_finditer(b"abc", 0, b"zabc", 2, None) == (
        "supported",
        2,
        4,
        [(2, 3)],
    )
    assert boundary.boundary_literal_subn("abc", 0, "x", "zabc", 3) == (
        "supported",
        "x",
        3,
    )
    assert boundary.boundary_escape(b"a-b") == b"a-b"

    assert boundary.calls == [
        ("compile", "abc", 4),
        ("match", "abc", 4, "search", "zabc", 1, None),
        ("split", b"abc", 2, b"zabc", 1),
        ("findall", "abc", 0, "zabc", 0, 4),
        ("finditer", b"abc", 0, b"zabc", 2, None),
        ("subn", "abc", 0, "x", "zabc", 3),
        ("escape", b"a-b"),
    ]


def test_recording_native_boundary_placeholder_helpers_follow_selected_message_source(
) -> None:
    boundary = RecordingNativeBoundary()

    with pytest.raises(NotImplementedError) as helper_raised:
        boundary.scaffold_raise("search")
    with pytest.raises(NotImplementedError) as pattern_raised:
        boundary.scaffold_pattern_raise("finditer")

    assert helper_raised.value.args == (rebar._placeholder_message("search"),)
    assert pattern_raised.value.args == (
        rebar._pattern_placeholder_message("finditer"),
    )

    native_boundary = RecordingNativeBoundary(native_placeholder_messages=True)
    with pytest.raises(NotImplementedError, match="native helper placeholder search"):
        native_boundary.scaffold_raise("search")
    with pytest.raises(NotImplementedError, match="native pattern placeholder finditer"):
        native_boundary.scaffold_pattern_raise("finditer")

    native_boundary.scaffold_purge()
    assert native_boundary.calls == [("purge",)]


def test_recording_native_boundary_missing_handlers_raise_clear_assertions() -> None:
    boundary = RecordingNativeBoundary()

    with pytest.raises(AssertionError, match="unexpected compile call"):
        boundary.boundary_compile("abc", 0)

    assert boundary.calls == [("compile", "abc", 0)]


@pytest.mark.parametrize(("selector", "expected_filenames"), SELECTOR_EXPECTATIONS)
def test_shared_correctness_fixture_selectors_resolve_expected_published_paths(
    selector: str,
    expected_filenames: tuple[str, ...],
) -> None:
    published_full_suite_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    selected_paths = select_correctness_fixture_paths(selector)

    assert tuple(path.name for path in selected_paths) == expected_filenames
    assert set(selected_paths).issubset(set(published_full_suite_paths))
    assert all(path.is_relative_to(CORRECTNESS_FIXTURES_ROOT) for path in selected_paths)


def test_unknown_correctness_fixture_selector_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="unknown correctness fixture selector"):
        select_correctness_fixture_paths("missing-selector")


def test_declared_correctness_fixture_selectors_match_registry_keys() -> None:
    declared_selectors = _declared_correctness_fixture_selectors()

    assert declared_selectors
    assert len(declared_selectors) == len(set(declared_selectors.values()))
    assert set(declared_selectors.values()) == set(
        correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR
    )


def test_selector_expectation_table_covers_declared_nondefault_selectors() -> None:
    declared_nondefault_selectors = set(_declared_correctness_fixture_selectors().values())
    declared_nondefault_selectors.remove(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)
    expected_selectors = tuple(
        selector for selector, _expected_filenames, _selector_id in SELECTOR_EXPECTATION_TABLE
    )

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


def test_default_fixture_inventory_has_unique_manifest_suite_and_case_ids() -> None:
    manifests = published_fixture_manifests()
    cases = [case for manifest in manifests for case in manifest.cases]

    assert published_fixture_manifests() is manifests
    assert tuple(manifest.path for manifest in manifests) == DEFAULT_FIXTURE_PATHS
    assert tuple(manifest.path.name for manifest in manifests) == tuple(
        path.name for path in DEFAULT_FIXTURE_PATHS
    )
    assert _duplicate_items(Counter(manifest.manifest_id for manifest in manifests)) == []
    assert _duplicate_items(Counter(manifest.suite_id for manifest in manifests)) == []
    assert _duplicate_items(Counter(case.case_id for case in cases)) == []

    cases_by_manifest = Counter(case.manifest_id for case in cases)
    manifest_ids = {manifest.manifest_id for manifest in manifests}

    for manifest in manifests:
        assert cases_by_manifest[manifest.manifest_id] > 0

    for case in cases:
        assert case.manifest_id in manifest_ids


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
        pytest.param(SYNTHETIC_MODULE_BYTES_SEARCH_CASE, id="module-bytes"),
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
    str_bundle, mixed_bundle = _load_fixture_bundles_from_root(
        tmp_path,
        (
            _bundle_loader_contract_str_spec(),
            _bundle_loader_contract_mixed_spec(),
        ),
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


def test_whole_manifest_bundle_contract_supports_expected_case_ids_and_fixture_path_validation(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    spec = _bundle_loader_contract_str_spec()
    (bundle,) = _load_fixture_bundles_from_root(tmp_path, (spec,))

    assert bundle.manifest.path == str_path
    assert bundle.expected_case_ids is not None
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
    )


def test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field(
    tmp_path: pathlib.Path,
) -> None:
    field_names = {field.name for field in fields(FixtureBundle)}
    _write_bundle_loader_contract_fixture_modules(tmp_path)
    (bundle,) = _load_fixture_bundles_from_root(
        tmp_path,
        (_bundle_loader_contract_str_spec(),),
    )

    assert "expected_manifest_id" not in field_names
    assert bundle.expected_manifest_id == BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID
    assert bundle.expected_manifest_id == bundle.manifest.manifest_id


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
    str_bundle, mixed_bundle = _load_fixture_bundles_from_root(
        tmp_path,
        (
            _bundle_loader_contract_str_spec(),
            _bundle_loader_contract_mixed_spec(),
        ),
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


def test_load_fixture_bundles_rejects_mismatched_expected_manifest_id(
    tmp_path: pathlib.Path,
) -> None:
    _write_bundle_loader_contract_fixture_modules(tmp_path)
    spec = _bundle_loader_contract_str_spec()

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"{BUNDLE_LOADER_CONTRACT_STR_FILENAME} expected_manifest_id "
            "'wrong-manifest-id' does not match loaded manifest_id "
            f"'{BUNDLE_LOADER_CONTRACT_STR_MANIFEST_ID}'"
        ),
    ):
        _load_fixture_bundles_from_root(
            tmp_path,
            (replace(spec, expected_manifest_id="wrong-manifest-id"),),
        )


def test_load_fixture_bundles_selected_case_ids_preserve_requested_order(
    tmp_path: pathlib.Path,
) -> None:
    selected_case_ids = (
        "bundle-loader-contract-compile-str",
        "bundle-loader-contract-pattern-search-str",
    )
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    spec = _bundle_loader_contract_str_spec()
    (bundle,) = _load_fixture_bundles_from_root(
        tmp_path,
        (
            replace(
                spec,
                selected_case_ids=selected_case_ids,
                expected_case_ids=None,
                expected_operation_helper_counts=Counter(
                    {
                        ("compile", None): 1,
                        ("pattern_call", "search"): 1,
                    }
                ),
            ),
        ),
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


def test_load_fixture_bundles_full_manifest_defaults_str_text_model_expectation(
    tmp_path: pathlib.Path,
) -> None:
    str_path, _ = _write_bundle_loader_contract_fixture_modules(tmp_path)
    spec = _bundle_loader_contract_str_spec()
    (bundle,) = _load_fixture_bundles_from_root(
        tmp_path,
        (replace(spec, expected_case_ids=None),),
    )

    assert bundle.expected_case_ids is None
    assert bundle.expected_text_models == frozenset({"str"})
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=str_path,
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
def test_load_fixture_bundles_rejects_invalid_selected_case_ids(
    tmp_path: pathlib.Path,
    selected_case_ids: tuple[str, ...],
    error_message: str,
) -> None:
    _write_bundle_loader_contract_fixture_modules(tmp_path)
    spec = _bundle_loader_contract_str_spec()

    with pytest.raises(ValueError, match=re.escape(error_message)):
        _load_fixture_bundles_from_root(
            tmp_path,
            (
                replace(
                    spec,
                    selected_case_ids=selected_case_ids,
                    expected_case_ids=None,
                ),
            ),
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
