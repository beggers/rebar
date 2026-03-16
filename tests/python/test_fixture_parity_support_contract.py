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
    SelectedCaseBundleSpec,
    WholeManifestBundleSpec,
    assert_fixture_bundle_contract,
    assert_finditer_parity,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    bundle_patterns,
    case_replacement_argument,
    case_pattern,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundle,
    load_selected_case_fixture_bundles,
    load_whole_manifest_fixture_bundles,
    load_published_fixture_bundles,
    load_published_fixture_cases,
    published_fixture_bundle_by_manifest_id,
    published_fixture_paths_from_bundles,
    raw_fixture_cases_by_id,
    select_published_fixture_cases_from_bundles,
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


def _selector_paths_matching_published_fixture_names(
    *,
    selector: str,
    filename_predicate,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    published_full_suite_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    selected_paths = select_correctness_fixture_paths(selector)
    expected_paths = tuple(
        sorted(
            (
                path
                for path in published_full_suite_paths
                if filename_predicate(path.name)
            ),
            key=lambda path: path.name,
        )
    )
    return (
        tuple(path.name for path in selected_paths),
        tuple(path.name for path in expected_paths),
    )


def _is_conditional_replacement_fixture_name(filename: str) -> bool:
    return (
        filename.startswith("conditional_group_exists_")
        and "_callable_" not in filename
        and (
            filename.endswith("_replacement_workflows.py")
            or filename.endswith("_replacement_template_workflows.py")
        )
    )


def _is_callable_replacement_fixture_name(filename: str) -> bool:
    return filename.endswith("_callable_replacement_workflows.py")


REPLACEMENT_SELECTOR_PATTERN_EXPECTATIONS = (
    pytest.param(
        CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
        _is_conditional_replacement_fixture_name,
        id="conditional-replacement",
    ),
    pytest.param(
        CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
        _is_callable_replacement_fixture_name,
        id="callable-replacement",
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


@pytest.mark.parametrize(
    ("selector", "filename_predicate"),
    REPLACEMENT_SELECTOR_PATTERN_EXPECTATIONS,
)
def test_replacement_family_selectors_follow_published_fixture_naming_conventions(
    selector: str,
    filename_predicate,
) -> None:
    selected_filenames, expected_filenames = (
        _selector_paths_matching_published_fixture_names(
            selector=selector,
            filename_predicate=filename_predicate,
        )
    )

    assert selected_filenames
    assert selected_filenames == expected_filenames


def test_case_pattern_helpers_extract_str_and_bytes_patterns_from_published_fixtures() -> None:
    module_case = NAMED_GROUP_CASES["named-group-module-search-metadata-str"]
    pattern_case = NAMED_GROUP_CASES["named-group-pattern-search-metadata-str"]
    bytes_case = COLLECTION_REPLACEMENT_CASES["pattern-split-bytes-maxsplit"]

    assert case_pattern(module_case) == r"(?P<word>abc)"
    assert str_case_pattern(module_case) == r"(?P<word>abc)"
    assert case_pattern(pattern_case) == r"(?P<word>abc)"
    assert str_case_pattern(pattern_case) == r"(?P<word>abc)"
    assert case_pattern(bytes_case) == b"abc"


def test_published_fixture_bundle_loading_preserves_selector_path_order() -> None:
    fixture_paths = tuple(
        reversed(select_correctness_fixture_paths(CALLABLE_REPLACEMENT_FIXTURE_SELECTOR)[:2])
    )

    bundles = load_published_fixture_bundles(fixture_paths)

    assert tuple(bundle.manifest.path for bundle in bundles) == fixture_paths
    for bundle in bundles:
        assert bundle.expected_case_ids is None
        assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_published_fixture_bundle_lookup_by_manifest_id_supports_success_and_clear_failures(
) -> None:
    bundles = load_published_fixture_bundles(
        select_correctness_fixture_paths(CALLABLE_REPLACEMENT_FIXTURE_SELECTOR)[:2]
    )
    manifest_id = bundles[0].manifest.manifest_id

    assert published_fixture_bundle_by_manifest_id(bundles, manifest_id) is bundles[0]

    with pytest.raises(
        ValueError,
        match=re.escape(
            "published fixture bundles do not contain manifest_id 'missing-manifest-id'"
        ),
    ):
        published_fixture_bundle_by_manifest_id(bundles, "missing-manifest-id")

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"published fixture bundles contain duplicate manifest_id {manifest_id!r}"
        ),
    ):
        published_fixture_bundle_by_manifest_id((bundles[0], bundles[0]), manifest_id)


def test_published_fixture_case_selection_preserves_requested_order_across_manifests(
) -> None:
    selected_case_ids = (
        "named-group-pattern-search-metadata-str",
        "grouped-module-fullmatch-two-capture-gap-str",
        "named-group-module-search-metadata-str",
    )

    cases = load_published_fixture_cases(
        select_correctness_fixture_paths(GROUPED_CAPTURE_FIXTURE_SELECTOR),
        selected_case_ids,
    )

    assert tuple(case.case_id for case in cases) == selected_case_ids
    assert tuple(case.manifest_id for case in cases) == (
        "named-group-workflows",
        "grouped-match-workflows",
        "named-group-workflows",
    )


def test_published_fixture_case_selection_rejects_missing_case_ids() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "selected published fixtures are missing case ids: ('missing-case-id',)"
        ),
    ):
        load_published_fixture_cases(
            select_correctness_fixture_paths(GROUPED_CAPTURE_FIXTURE_SELECTOR),
            (
                "named-group-pattern-search-metadata-str",
                "missing-case-id",
            ),
        )


def test_published_fixture_case_selection_rejects_duplicate_case_ids() -> None:
    duplicate_case_id = "grouped-module-fullmatch-two-capture-gap-str"
    grouped_match_fixture_path = FIXTURES_DIR / "grouped_match_workflows.py"

    with pytest.raises(
        ValueError,
        match=re.escape(
            "selected published fixtures contain duplicate case ids: "
            f"({duplicate_case_id!r},)"
        ),
    ):
        load_published_fixture_cases(
            (grouped_match_fixture_path, grouped_match_fixture_path),
            (duplicate_case_id,),
        )


def test_bundle_backed_published_fixture_case_selection_preserves_requested_order(
) -> None:
    bundles = load_selected_case_fixture_bundles(
        (
            SelectedCaseBundleSpec(
                fixture_name="grouped_match_workflows.py",
                expected_manifest_id="grouped-match-workflows",
                selected_case_ids=("grouped-module-fullmatch-two-capture-gap-str",),
                expected_patterns=frozenset({r"(ab)(c)"}),
                expected_operation_helper_counts=Counter(
                    {("module_call", "fullmatch"): 1}
                ),
                expected_text_models=frozenset({"str"}),
            ),
            SelectedCaseBundleSpec(
                fixture_name="named_group_workflows.py",
                expected_manifest_id="named-group-workflows",
                selected_case_ids=("named-group-compile-metadata-str",),
                expected_patterns=frozenset({r"(?P<word>abc)"}),
                expected_operation_helper_counts=Counter({("compile", None): 1}),
                expected_text_models=frozenset({"str"}),
            ),
        )
    )
    selected_case_ids = (
        "named-group-pattern-search-metadata-str",
        "grouped-module-search-single-capture-str",
        "grouped-pattern-fullmatch-two-capture-gap-str",
    )

    cases = select_published_fixture_cases_from_bundles(bundles, selected_case_ids)

    assert tuple(case.case_id for case in cases) == selected_case_ids
    assert tuple(case.manifest_id for case in cases) == (
        "named-group-workflows",
        "grouped-match-workflows",
        "grouped-match-workflows",
    )


def test_bundle_backed_published_fixture_case_selection_rejects_missing_case_ids() -> None:
    bundles = load_selected_case_fixture_bundles((_selected_case_bundle_specs()[1],))

    with pytest.raises(
        ValueError,
        match=re.escape(
            "selected published bundle cases are missing case ids: ('missing-case-id',)"
        ),
    ):
        select_published_fixture_cases_from_bundles(
            bundles,
            (
                "grouped-module-search-single-capture-str",
                "missing-case-id",
            ),
        )


def test_bundle_backed_published_fixture_case_selection_rejects_duplicate_case_ids(
) -> None:
    duplicate_case_id = "grouped-module-search-single-capture-str"
    bundles = load_selected_case_fixture_bundles((_selected_case_bundle_specs()[1],))

    with pytest.raises(
        ValueError,
        match=re.escape(
            "selected published bundle cases contain duplicate case ids: "
            f"({duplicate_case_id!r},)"
        ),
    ):
        select_published_fixture_cases_from_bundles(
            (bundles[0], bundles[0]),
            (duplicate_case_id,),
        )


def _whole_manifest_backreference_bundle_specs() -> tuple[WholeManifestBundleSpec, ...]:
    return (
        WholeManifestBundleSpec(
            fixture_name="named_backreference_workflows.py",
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
        ),
        WholeManifestBundleSpec(
            fixture_name="numbered_backreference_workflows.py",
            expected_manifest_id="numbered-backreference-workflows",
            expected_case_ids=frozenset(
                {
                    "numbered-backreference-compile-metadata-str",
                    "numbered-backreference-module-search-str",
                    "numbered-backreference-pattern-search-str",
                }
            ),
            expected_patterns=frozenset({r"(ab)\1"}),
            expected_operation_helper_counts=Counter(
                {
                    ("compile", None): 1,
                    ("module_call", "search"): 1,
                    ("pattern_call", "search"): 1,
                }
            ),
            expected_text_models=frozenset({"str"}),
        ),
    )


def _selected_case_bundle_specs() -> tuple[SelectedCaseBundleSpec, ...]:
    return (
        SelectedCaseBundleSpec(
            fixture_name="literal_flag_workflows.py",
            expected_manifest_id="literal-flag-workflows",
            selected_case_ids=(
                "flag-unsupported-inline-flag-search",
                "flag-unsupported-locale-bytes-search",
            ),
            expected_patterns=frozenset({"(?i)abc", b"abc"}),
            expected_operation_helper_counts=Counter({("module_call", "search"): 2}),
            expected_text_models=frozenset({"bytes", "str"}),
        ),
        SelectedCaseBundleSpec(
            fixture_name="grouped_match_workflows.py",
            expected_manifest_id="grouped-match-workflows",
            selected_case_ids=(
                "grouped-module-fullmatch-two-capture-gap-str",
                "grouped-pattern-fullmatch-two-capture-gap-str",
            ),
            expected_patterns=frozenset({r"(ab)(c)"}),
            expected_operation_helper_counts=Counter(
                {
                    ("module_call", "fullmatch"): 1,
                    ("pattern_call", "fullmatch"): 1,
                }
            ),
            expected_text_models=frozenset({"str"}),
        ),
    )


def test_whole_manifest_bundle_specs_load_in_declared_order_with_bundle_validation() -> None:
    bundles = load_whole_manifest_fixture_bundles(
        _whole_manifest_backreference_bundle_specs()
    )

    assert tuple(bundle.manifest.path.name for bundle in bundles) == (
        "named_backreference_workflows.py",
        "numbered_backreference_workflows.py",
    )
    for bundle in bundles:
        assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_fixture_case_fanout_from_bundles_preserves_bundle_then_case_order() -> None:
    bundles = load_whole_manifest_fixture_bundles(
        _whole_manifest_backreference_bundle_specs()
    )

    assert tuple(case.case_id for case in fixture_cases_from_bundles(bundles)) == (
        "named-backreference-compile-metadata-str",
        "named-backreference-module-search-str",
        "named-backreference-pattern-search-str",
        "numbered-backreference-compile-metadata-str",
        "numbered-backreference-module-search-str",
        "numbered-backreference-pattern-search-str",
    )


def test_fixture_case_operation_selection_preserves_published_row_order() -> None:
    bundles = load_whole_manifest_fixture_bundles(
        _whole_manifest_backreference_bundle_specs()
    )

    assert tuple(
        case.case_id for case in fixture_cases_for_operation(bundles, "pattern_call")
    ) == (
        "named-backreference-pattern-search-str",
        "numbered-backreference-pattern-search-str",
    )


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


def test_selected_case_bundle_specs_derive_exact_case_ids_and_preserve_case_order() -> None:
    (spec,) = _selected_case_bundle_specs()[:1]
    (bundle,) = load_selected_case_fixture_bundles((spec,))

    assert bundle.manifest.path == FIXTURES_DIR / spec.fixture_name
    assert bundle.expected_case_ids == frozenset(spec.selected_case_ids)
    assert tuple(case.case_id for case in bundle.cases) == spec.selected_case_ids
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


def test_selected_case_bundle_specs_load_in_declared_bundle_order() -> None:
    specs = tuple(reversed(_selected_case_bundle_specs()))

    bundles = load_selected_case_fixture_bundles(specs)

    assert tuple(bundle.manifest.path.name for bundle in bundles) == tuple(
        spec.fixture_name for spec in specs
    )
    for bundle in bundles:
        assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


def test_bundle_pattern_projection_and_raw_case_lookup_helpers_cover_published_fixtures() -> None:
    selected_case_ids = (
        "module-sub-callable-str",
        "module-sub-grouping-template",
    )
    bundle = load_fixture_bundle(
        "collection_replacement_workflows.py",
        expected_manifest_id="collection-replacement-workflows",
        expected_case_ids=frozenset(selected_case_ids),
        expected_patterns=frozenset({"abc", "(abc)"}),
        expected_operation_helper_counts=Counter({("module_call", "sub"): 2}),
        selected_case_ids=selected_case_ids,
        expected_text_models=frozenset({"str"}),
    )

    raw_cases = raw_fixture_cases_by_id(bundle)

    assert bundle_patterns(bundle, pattern_extractor=case_pattern) == frozenset(
        {"abc", "(abc)"}
    )
    assert bundle_patterns(bundle, pattern_extractor=str_case_pattern) == frozenset(
        {"abc", "(abc)"}
    )
    assert set(raw_cases) == set(selected_case_ids)
    assert raw_cases["module-sub-callable-str"]["args"][1] == {
        "type": "callable_constant",
        "value": "x",
    }
    assert raw_cases["module-sub-grouping-template"]["args"][1] == r"\1x"


def test_case_argument_helpers_cover_module_and_pattern_replacement_rows() -> None:
    module_bundle = load_fixture_bundle(
        "collection_replacement_workflows.py",
        expected_manifest_id="collection-replacement-workflows",
        expected_case_ids=frozenset({"module-sub-grouping-template"}),
        expected_patterns=frozenset({"(abc)"}),
        expected_operation_helper_counts=Counter({("module_call", "sub"): 1}),
        selected_case_ids=("module-sub-grouping-template",),
        expected_text_models=frozenset({"str"}),
    )
    pattern_bundle = load_fixture_bundle(
        "named_group_replacement_workflows.py",
        expected_manifest_id="named-group-replacement-workflows",
        expected_case_ids=frozenset({"pattern-sub-template-named-group-str"}),
        expected_patterns=frozenset({r"(?P<word>abc)"}),
        expected_operation_helper_counts=Counter({("pattern_call", "sub"): 1}),
        selected_case_ids=("pattern-sub-template-named-group-str",),
        expected_text_models=frozenset({"str"}),
    )

    module_case = module_bundle.cases[0]
    pattern_case = pattern_bundle.cases[0]

    assert case_replacement_argument(module_case) == module_case.args[1]
    assert case_text_argument(module_case) == module_case.args[2]
    assert case_replacement_argument(pattern_case) == pattern_case.args[0]
    assert case_text_argument(pattern_case) == pattern_case.args[1]


def test_module_workflow_surface_bundle_contract_covers_anchored_compile_case() -> None:
    bundle = load_fixture_bundle(
        "module_workflow_surface.py",
        expected_manifest_id="module-workflow-surface",
        expected_case_ids=frozenset(
            {
                "workflow-compile-str-literal",
                "workflow-compile-str-anchored-literal",
                "workflow-compile-bytes-literal",
                "workflow-pattern-search-str",
                "workflow-pattern-match-str",
                "workflow-pattern-fullmatch-bytes",
                "workflow-cache-hit-str",
                "workflow-cache-hit-bytes",
                "workflow-purge-reset-str",
                "workflow-escape-str",
                "workflow-escape-bytes",
            }
        ),
        expected_patterns=frozenset(
            {
                "abc",
                "^abc$",
                b"abc",
                b"123",
                "cache-me",
                b"cache-me",
                "purge-me",
                "a-b.c",
                b"a-b.c",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 3,
                ("pattern_call", "search"): 1,
                ("pattern_call", "match"): 1,
                ("pattern_call", "fullmatch"): 1,
                ("cache_workflow", None): 2,
                ("purge_workflow", None): 1,
                ("module_call", "escape"): 2,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    )

    assert bundle.manifest.path == FIXTURES_DIR / "module_workflow_surface.py"
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)
    assert "workflow-compile-str-anchored-literal" in {
        case.case_id for case in bundle.cases
    }


def test_module_workflow_surface_compile_case_selection_preserves_anchored_row_order() -> None:
    selected_case_ids = (
        "workflow-compile-str-literal",
        "workflow-compile-str-anchored-literal",
        "workflow-compile-bytes-literal",
    )
    (bundle,) = load_selected_case_fixture_bundles(
        (
            SelectedCaseBundleSpec(
                fixture_name="module_workflow_surface.py",
                expected_manifest_id="module-workflow-surface",
                selected_case_ids=selected_case_ids,
                expected_patterns=frozenset({"abc", "^abc$", b"abc"}),
                expected_operation_helper_counts=Counter({("compile", None): 3}),
                expected_text_models=frozenset({"bytes", "str"}),
            ),
        )
    )

    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)
    assert tuple(case.case_id for case in bundle.cases) == selected_case_ids
    assert tuple(case.case_id for case in fixture_cases_for_operation((bundle,), "compile")) == (
        selected_case_ids
    )


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
