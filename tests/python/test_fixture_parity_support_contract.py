from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import (
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    BOUNDED_WILDCARD_FIXTURE_SELECTOR,
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    COUNTED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    CORRECTNESS_FIXTURES_ROOT,
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
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    _match_api_templates,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    load_fixture_bundle,
    published_fixture_paths_from_bundles,
    str_case_pattern,
)
OPTIONAL_NAMED_GROUP_PATTERN = r"a(?P<word>b)?d"
BYTES_LITERAL_PATTERN = b"abc"
SELECTOR_EXPECTATIONS = (
    pytest.param(
        COUNTED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
        (
            "exact_repeat_quantified_group_workflows.py",
            "ranged_repeat_quantified_group_workflows.py",
        ),
        id="counted-repeat",
    ),
    pytest.param(
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
        id="quantified-alternation",
    ),
    pytest.param(
        BOUNDED_WILDCARD_FIXTURE_SELECTOR,
        (
            "collection_replacement_workflows.py",
            "literal_flag_workflows.py",
        ),
        id="bounded-wildcard",
    ),
    pytest.param(
        SIMPLE_BACKREFERENCE_FIXTURE_SELECTOR,
        (
            "named_backreference_workflows.py",
            "numbered_backreference_workflows.py",
        ),
        id="simple-backreference",
    ),
    pytest.param(
        CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
        (
            "conditional_group_exists_alternation_replacement_workflows.py",
            "conditional_group_exists_empty_else_replacement_workflows.py",
            "conditional_group_exists_empty_yes_else_replacement_workflows.py",
            "conditional_group_exists_fully_empty_replacement_workflows.py",
            "conditional_group_exists_nested_replacement_workflows.py",
            "conditional_group_exists_no_else_replacement_workflows.py",
            "conditional_group_exists_quantified_replacement_workflows.py",
            "conditional_group_exists_replacement_workflows.py",
        ),
        id="conditional-replacement",
    ),
    pytest.param(
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
        id="grouped-capture",
    ),
    pytest.param(
        WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
        (
            "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
            "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
            "broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
            "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
            "wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
            "wider_ranged_repeat_quantified_group_workflows.py",
        ),
        id="wider-ranged-repeat",
    ),
    pytest.param(
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
        id="branch-local-backreference",
    ),
    pytest.param(
        LITERAL_FLAG_FIXTURE_SELECTOR,
        ("literal_flag_workflows.py",),
        id="literal-flag",
    ),
    pytest.param(
        CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
        (
            "conditional_group_exists_callable_replacement_workflows.py",
            "grouped_alternation_callable_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py",
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "nested_group_alternation_callable_replacement_workflows.py",
            "nested_group_callable_replacement_workflows.py",
            "nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
            "quantified_nested_group_alternation_callable_replacement_workflows.py",
            "quantified_nested_group_callable_replacement_workflows.py",
        ),
        id="callable-replacement",
    ),
    pytest.param(
        OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
        (
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py",
            "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
            "nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
        ),
        id="open-ended-replacement-template",
    ),
    pytest.param(
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
        id="open-ended-quantified-group",
    ),
)


def _fixture_cases(fixture_name: str) -> dict[str, FixtureCase]:
    _, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return {case.case_id: case for case in cases}


NAMED_GROUP_CASES = _fixture_cases("named_group_workflows.py")
BRANCH_LOCAL_BACKREFERENCE_CASES = _fixture_cases(
    "branch_local_backreference_workflows.py"
)
COLLECTION_REPLACEMENT_CASES = _fixture_cases("collection_replacement_workflows.py")


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
        case = BRANCH_LOCAL_BACKREFERENCE_CASES[
            "branch-local-named-backreference-pattern-fullmatch-str"
        ]
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern_payload(),
            case.flags or 0,
        )
        return (
            observed_pattern.fullmatch(*case.args),
            expected_pattern.fullmatch(*case.args),
        )

    case = BRANCH_LOCAL_BACKREFERENCE_CASES[
        "branch-local-named-backreference-module-search-str"
    ]
    pattern = case_pattern(case)
    text = case.args[1]
    assert isinstance(pattern, str)
    assert isinstance(text, str)
    return (
        backend.search(pattern, text),
        re.search(pattern, text),
    )


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


def test_case_pattern_helpers_extract_str_and_bytes_patterns_from_published_fixtures() -> None:
    module_case = NAMED_GROUP_CASES["named-group-module-search-metadata-str"]
    pattern_case = NAMED_GROUP_CASES["named-group-pattern-search-metadata-str"]
    bytes_case = COLLECTION_REPLACEMENT_CASES["pattern-split-bytes-maxsplit"]

    assert case_pattern(module_case) == r"(?P<word>abc)"
    assert str_case_pattern(module_case) == r"(?P<word>abc)"
    assert case_pattern(pattern_case) == r"(?P<word>abc)"
    assert str_case_pattern(pattern_case) == r"(?P<word>abc)"
    assert case_pattern(bytes_case) == b"abc"


def test_whole_manifest_bundle_contract_supports_exact_case_id_validation() -> None:
    bundle = load_fixture_bundle(
        "named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "named-backreference-compile-metadata-str",
                "named-backreference-module-search-str",
                "named-backreference-pattern-search-str",
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

    assert bundle.manifest.path == FIXTURES_DIR / "named_backreference_workflows.py"
    assert bundle.expected_case_ids is not None
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_expected_fixture_bundle_contract_supports_exact_case_id_validation() -> None:
    bundle = load_fixture_bundle(
        "named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "named-backreference-compile-metadata-str",
                "named-backreference-module-search-str",
                "named-backreference-pattern-search-str",
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

    assert bundle.manifest.path == FIXTURES_DIR / "named_backreference_workflows.py"
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)
    assert published_fixture_paths_from_bundles((bundle,)) == (
        FIXTURES_DIR / "named_backreference_workflows.py",
    )


def test_expected_fixture_bundle_contract_supports_selected_case_loading() -> None:
    selected_case_ids = (
        "flag-unsupported-inline-flag-search",
        "flag-unsupported-locale-bytes-search",
    )
    bundle = load_fixture_bundle(
        "literal_flag_workflows.py",
        expected_manifest_id="literal-flag-workflows",
        expected_case_ids=frozenset(selected_case_ids),
        expected_patterns=frozenset({"(?i)abc", b"abc"}),
        expected_operation_helper_counts=Counter({("module_call", "search"): 2}),
        selected_case_ids=selected_case_ids,
    )

    assert bundle.manifest.path == FIXTURES_DIR / "literal_flag_workflows.py"
    assert tuple(case.case_id for case in bundle.cases) == selected_case_ids
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


def test_whole_manifest_bundle_contract_supports_full_manifest_counts_without_case_ids() -> None:
    named_bundle = load_fixture_bundle(
        "named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "named-backreference-compile-metadata-str",
                "named-backreference-module-search-str",
                "named-backreference-pattern-search-str",
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
    open_ended_bundle = load_fixture_bundle(
        "open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(bc|de){1,}d",
                r"a(?P<word>bc|de){1,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
    )

    assert open_ended_bundle.expected_case_ids is None
    assert_fixture_bundle_contract(
        open_ended_bundle,
        pattern_extractor=case_pattern,
    )
    assert tuple(
        path.name
        for path in published_fixture_paths_from_bundles((open_ended_bundle, named_bundle))
    ) == (
        "named_backreference_workflows.py",
        "open_ended_quantified_group_alternation_workflows.py",
    )


def test_match_api_templates_include_combined_named_group_templates() -> None:
    case = BRANCH_LOCAL_BACKREFERENCE_CASES[
        "branch-local-named-backreference-pattern-fullmatch-str"
    ]
    pattern = str_case_pattern(case)
    compiled = re.compile(pattern)

    templates = _match_api_templates(
        pattern,
        group_count=compiled.groups,
        group_names=tuple(compiled.groupindex),
    )

    assert r"<\g<outer>|\g<inner>>" in templates


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
