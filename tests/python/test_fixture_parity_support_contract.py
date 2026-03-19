from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields
import pathlib
import re
import textwrap
from types import SimpleNamespace

import pytest

import rebar
from rebar_harness.correctness import (
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    BOUNDED_WILDCARD_FIXTURE_SELECTOR,
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
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
from tests.python import conftest as python_conftest
from tests.python.conftest import _unsupported_backend_skip_reason
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    DIRECT_BYTES_FOLLOW_ON_SPEC_IDS,
    DIRECT_BYTES_FOLLOW_ON_SPECS,
    FIXTURES_DIR,
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    FixtureBundle,
    FixtureBundleSpec,
    RecordingNativeBoundary,
    SupplementalCase,
    assert_direct_bytes_follow_on_bundle_routing,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing,
    assert_finditer_parity,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    assert_valid_match_group_access_parity,
    bundle_patterns,
    case_replacement_argument,
    case_pattern,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    load_published_fixture_bundles,
    ordered_manifest_cases_from_bundles,
    partition_direct_bytes_follow_on_case_buckets,
    published_fixture_bundle_by_manifest_id,
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
            "broader_range_wider_ranged_repeat_quantified_group_workflows.py",
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
    pytest.param(
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
        id="conditional-replacement",
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
)
DIRECT_BYTES_FOLLOW_ON_MIXED_MANIFESTS = (
    pytest.param(
        "quantified_alternation_open_ended_workflows.py",
        id="open-ended-quantified-alternation",
    ),
    pytest.param(
        "quantified_alternation_branch_local_backreference_workflows.py",
        id="branch-local-quantified-alternation",
    ),
    pytest.param(
        "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
        id="branch-local-quantified-nested-group",
    ),
    pytest.param(
        (
            "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_"
            "branch_local_backreference_workflows.py"
        ),
        id="branch-local-nested-broader-range",
    ),
)


def _duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


def _tracked_fixture_paths() -> tuple[pathlib.Path, ...]:
    return tuple(sorted(FIXTURES_DIR.glob("*.py"), key=lambda path: path.name))


def _fixture_cases(fixture_name: str) -> dict[str, FixtureCase]:
    manifest = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return {case.case_id: case for case in manifest.cases}


def _write_fixture_module(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


NAMED_GROUP_CASES = _fixture_cases("named_group_workflows.py")
BRANCH_LOCAL_BACKREFERENCE_CASES = _fixture_cases(
    "branch_local_backreference_workflows.py"
)
COLLECTION_REPLACEMENT_CASES = _fixture_cases("collection_replacement_workflows.py")


@dataclass(frozen=True)
class FakeParityCase:
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


def _request_with_params(**params: object) -> object:
    return SimpleNamespace(node=SimpleNamespace(callspec=SimpleNamespace(params=params)))


def _fixture_request(backend_name: str, **params: object) -> object:
    return SimpleNamespace(
        param=backend_name,
        node=SimpleNamespace(callspec=SimpleNamespace(params=params)),
    )


def test_unsupported_backend_skip_reason_ignores_requests_without_callspec() -> None:
    request = SimpleNamespace(node=SimpleNamespace())

    assert _unsupported_backend_skip_reason(request, "rebar") is None


def test_unsupported_backend_skip_reason_preserves_case_param_compatibility() -> None:
    request = _request_with_params(
        case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="case-style reason",
        )
    )

    assert _unsupported_backend_skip_reason(request, "rebar") == "case-style reason"


def test_unsupported_backend_skip_reason_supports_nonstandard_case_param_names() -> None:
    request = _request_with_params(
        supplemental_case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="supplemental reason",
        )
    )

    assert _unsupported_backend_skip_reason(request, "rebar") == "supplemental reason"


def test_unsupported_backend_skip_reason_ignores_unrelated_params() -> None:
    request = _request_with_params(
        text="abc",
        flags=0,
        supplemental_case=FakeParityCase(unsupported_backends=("stdlib",)),
    )

    assert _unsupported_backend_skip_reason(request, "rebar") is None


def test_unsupported_backend_skip_reason_defaults_missing_reason() -> None:
    request = _request_with_params(
        supplemental_case=FakeParityCase(unsupported_backends=("rebar",))
    )

    assert (
        _unsupported_backend_skip_reason(request, "rebar")
        == "rebar backend unsupported for this parity case"
    )


def test_unsupported_backend_skip_reason_rejects_multiple_param_sources() -> None:
    request = _request_with_params(
        case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="primary reason",
        ),
        supplemental_case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="secondary reason",
        ),
    )

    with pytest.raises(
        AssertionError,
        match="multiple parametrized values declare unsupported_backends",
    ):
        _unsupported_backend_skip_reason(request, "rebar")


def test_purge_regex_caches_calls_both_backends_before_and_after_test(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def _record_stdlib_purge() -> None:
        calls.append("stdlib")

    def _record_rebar_purge() -> None:
        calls.append("rebar")

    monkeypatch.setattr(python_conftest.re, "purge", _record_stdlib_purge)
    monkeypatch.setattr(python_conftest.rebar, "purge", _record_rebar_purge)

    fixture_gen = python_conftest.purge_regex_caches.__wrapped__()

    next(fixture_gen)
    assert calls == ["stdlib", "rebar"]

    with pytest.raises(StopIteration):
        next(fixture_gen)

    assert calls == ["stdlib", "rebar", "stdlib", "rebar"]


def test_regex_backend_fixture_returns_stdlib_backend_module() -> None:
    request = _fixture_request("stdlib")

    assert python_conftest.regex_backend.__wrapped__(request) == ("stdlib", re)


@pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="rebar backend fixture only resolves when rebar._rebar is available",
)
def test_regex_backend_fixture_returns_rebar_backend_module() -> None:
    request = _fixture_request("rebar")

    assert python_conftest.regex_backend.__wrapped__(request) == ("rebar", rebar)


def test_regex_backend_fixture_propagates_unsupported_backend_skips() -> None:
    request = _fixture_request(
        "rebar",
        case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="feature slice is stdlib-only",
        ),
    )

    with pytest.raises(pytest.skip.Exception, match="feature slice is stdlib-only"):
        python_conftest.regex_backend.__wrapped__(request)


@pytest.mark.parametrize(
    ("supplemental_cases", "expected_case_ids"),
    (
        pytest.param(
            OPEN_ENDED_ALTERNATION_BYTES_CASES,
            (
                "open-ended-grouped-alternation-numbered-bytes",
                "open-ended-grouped-alternation-named-bytes",
            ),
            id="open-ended-alternation",
        ),
        pytest.param(
            NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
            (
                "nested-open-ended-grouped-alternation-numbered-bytes",
                "nested-open-ended-grouped-alternation-named-bytes",
            ),
            id="nested-open-ended-alternation",
        ),
        pytest.param(
            OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            (
                "open-ended-grouped-conditional-numbered-bytes",
                "open-ended-grouped-conditional-named-bytes",
            ),
            id="open-ended-conditional",
        ),
        pytest.param(
            OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            (
                "open-ended-grouped-backtracking-heavy-numbered-bytes",
                "open-ended-grouped-backtracking-heavy-named-bytes",
            ),
            id="open-ended-backtracking-heavy",
        ),
        pytest.param(
            BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
            (
                "broader-range-open-ended-grouped-alternation-numbered-bytes",
                "broader-range-open-ended-grouped-alternation-named-bytes",
            ),
            id="broader-range-open-ended-alternation",
        ),
        pytest.param(
            BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
            (
                "broader-range-open-ended-grouped-conditional-numbered-bytes",
                "broader-range-open-ended-grouped-conditional-named-bytes",
            ),
            id="broader-range-open-ended-conditional",
        ),
        pytest.param(
            BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            (
                "broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes",
                "broader-range-open-ended-grouped-backtracking-heavy-named-bytes",
            ),
            id="broader-range-open-ended-backtracking-heavy",
        ),
    ),
)
def test_open_ended_supplemental_bytes_case_tables_keep_case_ids_in_order(
    supplemental_cases: tuple[SupplementalCase, ...],
    expected_case_ids: tuple[str, ...],
) -> None:
    assert tuple(case.id for case in supplemental_cases) == expected_case_ids


def test_open_ended_direct_bytes_follow_on_specs_keep_expected_manifest_pairings(
) -> None:
    assert DIRECT_BYTES_FOLLOW_ON_SPEC_IDS == (
        "broader-range-alternation",
        "open-ended-backtracking-heavy",
        "broader-range-conditional",
        "broader-range-backtracking-heavy",
    )
    assert tuple((spec.id, spec.manifest_id) for spec in DIRECT_BYTES_FOLLOW_ON_SPECS) == (
        (
            "broader-range-alternation",
            "broader-range-open-ended-quantified-group-alternation-workflows",
        ),
        (
            "open-ended-backtracking-heavy",
            "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        ),
        (
            "broader-range-conditional",
            "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
        ),
        (
            "broader-range-backtracking-heavy",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        ),
    )
    assert (
        DIRECT_BYTES_FOLLOW_ON_SPECS[0].supplemental_cases
        is BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES
    )
    assert (
        DIRECT_BYTES_FOLLOW_ON_SPECS[1].supplemental_cases
        is OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    )
    assert (
        DIRECT_BYTES_FOLLOW_ON_SPECS[2].supplemental_cases
        is BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES
    )
    assert (
        DIRECT_BYTES_FOLLOW_ON_SPECS[3].supplemental_cases
        is BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES
    )


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


def test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory() -> None:
    published_fixture_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )
    tracked_fixture_paths = _tracked_fixture_paths()

    assert DEFAULT_FIXTURE_PATHS == published_fixture_paths
    assert set(published_fixture_paths) == set(tracked_fixture_paths)
    assert len(published_fixture_paths) == len(set(published_fixture_paths))

    for path in published_fixture_paths:
        assert path.is_relative_to(FIXTURES_DIR)
        assert path.is_file()
        assert path.suffix == ".py"


def test_published_full_suite_fixture_selector_preserves_explicit_manifest_order() -> None:
    published_fixture_paths = select_correctness_fixture_paths(
        PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
    )

    assert tuple(path.name for path in published_fixture_paths) == tuple(
        path.name for path in DEFAULT_FIXTURE_PATHS
    )


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


def test_published_fixture_bundle_loading_preserves_mixed_text_model_contract() -> None:
    fixture_path = (
        FIXTURES_DIR
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )

    (bundle,) = load_published_fixture_bundles((fixture_path,))

    assert bundle.manifest.manifest_id == (
        "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
    )
    assert bundle.expected_case_ids is None
    assert bundle.expected_text_models == frozenset({"bytes", "str"})
    assert bundle.expected_patterns == frozenset(
        {
            r"a((bc|de){1,4})?(?(1)d|e)",
            r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
            rb"a((bc|de){1,4})?(?(1)d|e)",
            rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        }
    )
    assert Counter((case.operation, case.helper) for case in bundle.cases) == Counter(
        {
            ("compile", None): 4,
            ("module_call", "search"): 12,
            ("pattern_call", "fullmatch"): 12,
        }
    )
    assert tuple(case.case_id for case in bundle.cases) == tuple(
        case.case_id for case in bundle.manifest.cases
    )
    assert {
        isinstance(case_pattern(case), str)
        for case in bundle.cases
        if case.text_model == "str"
    } == {True}
    assert {
        isinstance(case_pattern(case), bytes)
        for case in bundle.cases
        if case.text_model == "bytes"
    } == {True}

    str_case_ids = frozenset(
        case.case_id for case in bundle.cases if case.text_model == "str"
    )
    bytes_case_ids = frozenset(
        case.case_id for case in bundle.cases if case.text_model == "bytes"
    )

    assert len(str_case_ids) == len(bytes_case_ids) == 14
    assert bytes_case_ids == {
        f"{case_id.removesuffix('-str')}-bytes" for case_id in str_case_ids
    }
    assert published_fixture_paths_from_bundles((bundle,)) == (fixture_path,)
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=fixture_path,
    )


@pytest.mark.parametrize("fixture_name", DIRECT_BYTES_FOLLOW_ON_MIXED_MANIFESTS)
def test_assert_direct_bytes_follow_on_bundle_routing_accepts_mixed_manifest_buckets(
    fixture_name: str,
) -> None:
    fixture_path = FIXTURES_DIR / fixture_name
    (bundle,) = load_published_fixture_bundles((fixture_path,))
    compile_cases, module_cases, pattern_cases = (
        partition_direct_bytes_follow_on_case_buckets((bundle,), (bundle,))
    )

    bundle_str_cases, bundle_bytes_cases = assert_direct_bytes_follow_on_bundle_routing(
        bundle,
        compile_cases=compile_cases,
        module_cases=module_cases,
        pattern_cases=pattern_cases,
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
    fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    (bundle,) = load_published_fixture_bundles((fixture_path,))
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
        assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )


def test_assert_direct_bytes_follow_on_bundle_routing_rejects_missing_str_rows() -> None:
    fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    (bundle,) = load_published_fixture_bundles((fixture_path,))
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
        assert_direct_bytes_follow_on_bundle_routing(
            bundle,
            compile_cases=compile_cases,
            module_cases=module_cases,
            pattern_cases=pattern_cases,
        )


def test_mixed_text_model_manifest_helper_accepts_exact_direct_follow_on_coverage(
) -> None:
    mixed_fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    str_only_fixture_path = FIXTURES_DIR / "grouped_match_workflows.py"
    mixed_bundle, str_only_bundle = load_published_fixture_bundles(
        (mixed_fixture_path, str_only_fixture_path)
    )

    assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(
        (mixed_bundle, str_only_bundle),
        direct_bytes_follow_on_bundles=(mixed_bundle,),
        coverage_label="fixture parity support contract",
    )


def test_mixed_text_model_manifest_helper_reports_missing_direct_follow_on_bundle(
) -> None:
    mixed_fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    str_only_fixture_path = FIXTURES_DIR / "grouped_match_workflows.py"
    mixed_bundle, str_only_bundle = load_published_fixture_bundles(
        (mixed_fixture_path, str_only_fixture_path)
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract direct bytes follow-on manifest routing "
            "drifted; missing mixed manifests: "
            "('quantified-alternation-open-ended-workflows',); "
            "unexpected direct manifests: ()"
        ),
    ):
        assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(
            (mixed_bundle, str_only_bundle),
            direct_bytes_follow_on_bundles=(),
            coverage_label="fixture parity support contract",
        )


def test_mixed_text_model_manifest_helper_reports_unexpected_direct_follow_on_bundle(
) -> None:
    mixed_fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    str_only_fixture_path = FIXTURES_DIR / "grouped_match_workflows.py"
    mixed_bundle, str_only_bundle = load_published_fixture_bundles(
        (mixed_fixture_path, str_only_fixture_path)
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract direct bytes follow-on manifest routing "
            "drifted; missing mixed manifests: "
            "('quantified-alternation-open-ended-workflows',); "
            "unexpected direct manifests: ('grouped-match-workflows',)"
        ),
    ):
        assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(
            (mixed_bundle, str_only_bundle),
            direct_bytes_follow_on_bundles=(str_only_bundle,),
            coverage_label="fixture parity support contract",
        )


def test_mixed_text_model_manifest_helper_reports_direct_follow_on_order_drift(
) -> None:
    first_mixed_fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    second_mixed_fixture_path = (
        FIXTURES_DIR / "broader_range_open_ended_quantified_group_alternation_workflows.py"
    )
    first_bundle, second_bundle = load_published_fixture_bundles(
        (first_mixed_fixture_path, second_mixed_fixture_path)
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "fixture parity support contract direct bytes follow-on manifest order "
            "drifted; expected "
            "('quantified-alternation-open-ended-workflows', "
            "'broader-range-open-ended-quantified-group-alternation-workflows'), "
            "got ('broader-range-open-ended-quantified-group-alternation-workflows', "
            "'quantified-alternation-open-ended-workflows')"
        ),
    ):
        assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(
            (first_bundle, second_bundle),
            direct_bytes_follow_on_bundles=(second_bundle, first_bundle),
            coverage_label="fixture parity support contract",
        )


@pytest.mark.parametrize("fixture_name", DIRECT_BYTES_FOLLOW_ON_MIXED_MANIFESTS)
def test_partition_direct_bytes_follow_on_case_buckets_drops_only_follow_on_bytes_rows(
    fixture_name: str,
) -> None:
    fixture_path = FIXTURES_DIR / fixture_name
    (bundle,) = load_published_fixture_bundles((fixture_path,))

    compile_cases, module_cases, pattern_cases = (
        partition_direct_bytes_follow_on_case_buckets((bundle,), (bundle,))
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
    follow_on_fixture_path = FIXTURES_DIR / "quantified_alternation_open_ended_workflows.py"
    preserved_fixture_path = (
        FIXTURES_DIR
        / "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py"
    )
    follow_on_bundle, preserved_bundle = load_published_fixture_bundles(
        (follow_on_fixture_path, preserved_fixture_path)
    )

    compile_cases, module_cases, pattern_cases = (
        partition_direct_bytes_follow_on_case_buckets(
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


def test_fixture_manifest_loader_materializes_callable_replacement_descriptors(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_fixture_module(
        tmp_path,
        "quantified_nested_group_callable_fixture.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "quantified-nested-group-callable-loader-contract",
            "layer": "module_workflow",
            "suite_id": "collection.replacement.quantified_nested_group.callable.contract",
            "defaults": {
                "text_model": "str",
            },
            "cases": [
                {
                    "id": "module-sub-callable-numbered-contract-str",
                    "operation": "module_call",
                    "family": "quantified_nested_group_numbered_callable_contract",
                    "helper": "sub",
                    "args": [
                        r"a((bc)+)d",
                        {
                            "type": "callable_match_group",
                            "group": 1,
                            "suffix": "x",
                        },
                        "zzabcbcdzz",
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "str"],
                    "notes": [
                        "Ensures Python-backed fixtures can materialize numbered callable replacement descriptors for quantified nested-group workflows."
                    ],
                },
                {
                    "id": "pattern-subn-callable-named-contract-str",
                    "operation": "pattern_call",
                    "family": "quantified_nested_group_named_callable_contract",
                    "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                    "helper": "subn",
                    "args": [
                        {
                            "type": "callable_match_group",
                            "group": "inner",
                            "prefix": "<",
                            "suffix": ">",
                        },
                        "zzabcbcdabcbcdzz",
                        1,
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "str"],
                    "notes": [
                        "Ensures Python-backed fixtures can materialize named callable replacement descriptors for quantified nested-group workflows."
                    ],
                },
                {
                    "id": "module-sub-callable-constant-contract-str",
                    "operation": "module_call",
                    "family": "quantified_nested_group_constant_callable_contract",
                    "helper": "sub",
                    "args": [
                        r"a((bc)+)d",
                        {
                            "type": "callable_constant",
                            "value": "CONST",
                        },
                        "zzabcdzz",
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "str"],
                    "notes": [
                        "Ensures Python-backed fixtures can materialize constant callable descriptors without falling back to raw dict payloads."
                    ],
                },
            ],
        }
        """,
    )

    manifest = load_fixture_manifest(fixture_path)
    cases = manifest.cases

    assert manifest.manifest_id == "quantified-nested-group-callable-loader-contract"
    assert manifest.layer == "module_workflow"
    assert (
        manifest.suite_id
        == "collection.replacement.quantified_nested_group.callable.contract"
    )
    assert [case.case_id for case in cases] == [
        "module-sub-callable-numbered-contract-str",
        "pattern-subn-callable-named-contract-str",
        "module-sub-callable-constant-contract-str",
    ]

    numbered_case = cases[0]
    assert numbered_case.helper == "sub"
    assert numbered_case.args[0] == r"a((bc)+)d"
    assert numbered_case.source_args == [
        r"a((bc)+)d",
        {
            "type": "callable_match_group",
            "group": 1,
            "suffix": "x",
        },
        "zzabcbcdzz",
    ]
    assert numbered_case.source_kwargs == {}
    assert callable(numbered_case.args[1])
    numbered_match = re.search(r"a((bc)+)d", "zzabcbcdzz")
    assert numbered_match is not None
    assert numbered_case.args[1](numbered_match) == "bcbcx"
    assert numbered_case.serialized_args()[1] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_match_group",
    }

    named_case = cases[1]
    assert named_case.helper == "subn"
    assert named_case.pattern_payload() == r"a(?P<outer>(?P<inner>bc)+)d"
    assert named_case.source_args == [
        {
            "type": "callable_match_group",
            "group": "inner",
            "prefix": "<",
            "suffix": ">",
        },
        "zzabcbcdabcbcdzz",
        1,
    ]
    assert named_case.source_kwargs == {}
    assert callable(named_case.args[0])
    named_match = re.search(named_case.pattern_payload(), "zzabcbcdzz")
    assert named_match is not None
    assert named_case.args[0](named_match) == "<bc>"
    assert named_case.serialized_args()[0] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_match_group",
    }

    constant_case = cases[2]
    assert constant_case.helper == "sub"
    assert constant_case.source_args == [
        r"a((bc)+)d",
        {
            "type": "callable_constant",
            "value": "CONST",
        },
        "zzabcdzz",
    ]
    assert constant_case.source_kwargs == {}
    assert callable(constant_case.args[1])
    constant_match = re.search(r"a((bc)+)d", "zzabcdzz")
    assert constant_match is not None
    assert constant_case.args[1](constant_match) == "CONST"
    assert constant_case.serialized_args()[1] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_constant",
    }


def test_fixture_manifest_loader_materializes_bytes_callables_without_aliasing_defaults(
    tmp_path: pathlib.Path,
) -> None:
    fixture_path = _write_fixture_module(
        tmp_path,
        "bytes_callable_fixture.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "bytes-callable-loader-contract",
            "layer": "module_workflow",
            "suite_id": "collection.replacement.bytes.callable.contract",
            "defaults": {
                "operation": "pattern_call",
                "helper": "sub",
                "text_model": "bytes",
                "pattern_encoding": "latin-1",
                "args": [
                    {
                        "type": "callable_match_group",
                        "group": 1,
                        "prefix": {
                            "type": "bytes",
                            "value": "<",
                        },
                        "suffix": {
                            "type": "bytes",
                            "value": ">",
                        },
                    },
                    {
                        "type": "bytes",
                        "value": "zzabcbcdzz",
                    },
                ],
                "kwargs": {
                    "count": 1,
                },
            },
            "cases": [
                {
                    "id": "pattern-sub-callable-match-group-default-a-bytes",
                    "family": "bytes_callable_match_group_default",
                    "pattern": r"a((bc)+)d",
                },
                {
                    "id": "pattern-sub-callable-match-group-default-b-bytes",
                    "family": "bytes_callable_match_group_default",
                    "pattern": r"a((bc)+)d",
                },
                {
                    "id": "pattern-sub-callable-constant-override-bytes",
                    "family": "bytes_callable_constant_override",
                    "pattern": r"a((bc)+)d",
                    "args": [
                        {
                            "type": "callable_constant",
                            "value": {
                                "type": "bytes",
                                "value": "CONST",
                            },
                        },
                        {
                            "type": "bytes",
                            "value": "zzabcbcdzz",
                        },
                    ],
                },
            ],
        }
        """,
    )

    manifest = load_fixture_manifest(fixture_path)
    cases = manifest.cases

    assert manifest.manifest_id == "bytes-callable-loader-contract"
    assert manifest.layer == "module_workflow"
    assert manifest.suite_id == "collection.replacement.bytes.callable.contract"
    assert [case.case_id for case in cases] == [
        "pattern-sub-callable-match-group-default-a-bytes",
        "pattern-sub-callable-match-group-default-b-bytes",
        "pattern-sub-callable-constant-override-bytes",
    ]

    first_default_case, second_default_case, constant_case = cases

    assert first_default_case.pattern_payload() == b"a((bc)+)d"
    assert second_default_case.pattern_payload() == b"a((bc)+)d"
    assert constant_case.pattern_payload() == b"a((bc)+)d"

    assert first_default_case.args is not second_default_case.args
    assert first_default_case.kwargs is not second_default_case.kwargs
    assert first_default_case.source_args is not second_default_case.source_args
    assert first_default_case.source_kwargs is not second_default_case.source_kwargs
    assert first_default_case.source_args == [
        {
            "type": "callable_match_group",
            "group": 1,
            "prefix": {
                "type": "bytes",
                "value": "<",
            },
            "suffix": {
                "type": "bytes",
                "value": ">",
            },
        },
        {
            "type": "bytes",
            "value": "zzabcbcdzz",
        },
    ]
    assert first_default_case.source_kwargs == {"count": 1}
    assert second_default_case.source_args == [
        {
            "type": "callable_match_group",
            "group": 1,
            "prefix": {
                "type": "bytes",
                "value": "<",
            },
            "suffix": {
                "type": "bytes",
                "value": ">",
            },
        },
        {
            "type": "bytes",
            "value": "zzabcbcdzz",
        },
    ]
    assert second_default_case.source_kwargs == {"count": 1}
    assert callable(first_default_case.args[0])
    assert callable(second_default_case.args[0])
    assert first_default_case.args[0] is not second_default_case.args[0]
    assert first_default_case.source_args[0] is not second_default_case.source_args[0]
    assert first_default_case.args[1] == b"zzabcbcdzz"
    assert first_default_case.serialized_args() == [
        {
            "type": "callable",
            "module": "rebar_harness.correctness",
            "qualname": "callable_match_group",
        },
        {
            "encoding": "latin-1",
            "value": "zzabcbcdzz",
        },
    ]
    assert first_default_case.serialized_kwargs() == {"count": 1}

    match = re.search(first_default_case.pattern_payload(), first_default_case.args[1])
    assert match is not None
    assert first_default_case.args[0](match) == b"<bcbc>"

    first_default_case.args[1] = b"mutated"
    first_default_case.kwargs["count"] = 0
    first_default_case.source_args[0]["prefix"]["value"] = "["
    first_default_case.source_args[1]["value"] = "mutated-source"
    first_default_case.source_kwargs["count"] = 0
    assert second_default_case.args[1] == b"zzabcbcdzz"
    assert second_default_case.kwargs["count"] == 1
    assert second_default_case.source_args[0]["prefix"]["value"] == "<"
    assert second_default_case.source_args[1]["value"] == "zzabcbcdzz"
    assert second_default_case.source_kwargs["count"] == 1
    assert constant_case.kwargs["count"] == 1
    assert constant_case.source_kwargs["count"] == 1

    assert callable(constant_case.args[0])
    assert constant_case.source_args == [
        {
            "type": "callable_constant",
            "value": {
                "type": "bytes",
                "value": "CONST",
            },
        },
        {
            "type": "bytes",
            "value": "zzabcbcdzz",
        },
    ]
    constant_match = re.search(constant_case.pattern_payload(), constant_case.args[1])
    assert constant_match is not None
    assert constant_case.args[0](constant_match) == b"CONST"
    assert constant_case.serialized_args()[0] == {
        "type": "callable",
        "module": "rebar_harness.correctness",
        "qualname": "callable_constant",
    }
    assert constant_case.serialized_args()[1] == {
        "encoding": "latin-1",
        "value": "zzabcbcdzz",
    }


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


def _whole_manifest_backreference_bundle_specs() -> tuple[FixtureBundleSpec, ...]:
    return (
        FixtureBundleSpec(
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
        FixtureBundleSpec(
            fixture_name="numbered_backreference_workflows.py",
            expected_manifest_id="numbered-backreference-workflows",
            expected_case_ids=frozenset(
                {
                    "numbered-backreference-compile-metadata-str",
                    "numbered-backreference-module-search-str",
                    "numbered-backreference-pattern-search-str",
                    "numbered-backreference-segment-module-search-str",
                    "numbered-backreference-prefix-pattern-search-str",
                }
            ),
            expected_patterns=frozenset({r"(ab)\1", r"(ab)x\1", r"x(ab)\1"}),
            expected_operation_helper_counts=Counter(
                {
                    ("compile", None): 1,
                    ("module_call", "search"): 2,
                    ("pattern_call", "search"): 2,
                }
            ),
            expected_text_models=frozenset({"str"}),
        ),
    )


def _selected_case_bundle_specs() -> tuple[FixtureBundleSpec, ...]:
    return (
        FixtureBundleSpec(
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
        FixtureBundleSpec(
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
    bundles = load_fixture_bundles(
        _whole_manifest_backreference_bundle_specs()
    )

    assert tuple(bundle.manifest.path.name for bundle in bundles) == (
        "named_backreference_workflows.py",
        "numbered_backreference_workflows.py",
    )
    for bundle in bundles:
        assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_fixture_case_fanout_from_bundles_preserves_bundle_then_case_order() -> None:
    bundles = load_fixture_bundles(
        _whole_manifest_backreference_bundle_specs()
    )

    assert tuple(case.case_id for case in fixture_cases_from_bundles(bundles)) == (
        "named-backreference-compile-metadata-str",
        "named-backreference-module-search-str",
        "named-backreference-pattern-search-str",
        "numbered-backreference-compile-metadata-str",
        "numbered-backreference-module-search-str",
        "numbered-backreference-pattern-search-str",
        "numbered-backreference-segment-module-search-str",
        "numbered-backreference-prefix-pattern-search-str",
    )


def test_fixture_case_operation_selection_preserves_published_row_order() -> None:
    bundles = load_fixture_bundles(
        _whole_manifest_backreference_bundle_specs()
    )

    assert tuple(
        case.case_id for case in fixture_cases_for_operation(bundles, "pattern_call")
    ) == (
        "named-backreference-pattern-search-str",
        "numbered-backreference-pattern-search-str",
        "numbered-backreference-prefix-pattern-search-str",
    )


def test_whole_manifest_bundle_contract_supports_exact_case_id_validation() -> None:
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
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
            ),
        )
    )

    assert bundle.manifest.path == FIXTURES_DIR / "named_backreference_workflows.py"
    assert bundle.expected_case_ids is not None
    assert_fixture_bundle_contract(bundle, pattern_extractor=str_case_pattern)


def test_expected_fixture_bundle_contract_supports_exact_case_id_validation() -> None:
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
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
            ),
        )
    )

    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
        expected_fixture_path=FIXTURES_DIR / "named_backreference_workflows.py",
    )
    assert published_fixture_paths_from_bundles((bundle,)) == (
        FIXTURES_DIR / "named_backreference_workflows.py",
    )


def test_fixture_bundle_contract_supports_selected_case_path_and_order_validation() -> None:
    (spec,) = _selected_case_bundle_specs()[:1]
    (bundle,) = load_fixture_bundles((spec,))

    assert bundle.expected_case_ids == frozenset(spec.selected_case_ids)
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=FIXTURES_DIR / spec.fixture_name,
        expected_ordered_case_ids=spec.selected_case_ids,
    )


def test_fixture_bundle_exposes_derived_manifest_id_without_storing_duplicate_field() -> None:
    field_names = {field.name for field in fields(FixtureBundle)}
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
                fixture_name="named_backreference_workflows.py",
                expected_manifest_id="named-backreference-workflows",
                expected_patterns=frozenset({r"(?P<word>ab)(?P=word)"}),
                expected_operation_helper_counts=Counter(
                    {
                        ("compile", None): 1,
                        ("module_call", "search"): 1,
                        ("pattern_call", "search"): 1,
                    }
                ),
            ),
        )
    )

    assert "expected_manifest_id" not in field_names
    assert bundle.expected_manifest_id == "named-backreference-workflows"
    assert bundle.expected_manifest_id == bundle.manifest.manifest_id


def test_load_fixture_bundles_rejects_duplicate_selected_case_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "literal_flag_workflows.py selected_case_ids contains duplicate ids: "
            "\\('flag-unsupported-inline-flag-search',\\)"
        ),
    ):
        load_fixture_bundles(
            (
                FixtureBundleSpec(
                    fixture_name="literal_flag_workflows.py",
                    expected_manifest_id="literal-flag-workflows",
                    selected_case_ids=(
                        "flag-unsupported-inline-flag-search",
                        "flag-unsupported-inline-flag-search",
                    ),
                    expected_patterns=frozenset({"(?i)abc"}),
                    expected_operation_helper_counts=Counter(
                        {("module_call", "search"): 2}
                    ),
                    expected_text_models=frozenset({"str"}),
                ),
            )
        )


def test_load_fixture_bundles_rejects_empty_selected_case_ids() -> None:
    with pytest.raises(
        ValueError,
        match="literal_flag_workflows.py selected_case_ids must not be empty",
    ):
        load_fixture_bundles(
            (
                FixtureBundleSpec(
                    fixture_name="literal_flag_workflows.py",
                    expected_manifest_id="literal-flag-workflows",
                    selected_case_ids=(),
                    expected_patterns=frozenset(),
                    expected_operation_helper_counts=Counter(),
                ),
            )
        )


def test_load_fixture_bundles_rejects_mismatched_expected_manifest_id() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "named_backreference_workflows.py expected_manifest_id "
            "'wrong-manifest-id' does not match loaded manifest_id "
            "'named-backreference-workflows'"
        ),
    ):
        load_fixture_bundles(
            (
                FixtureBundleSpec(
                    fixture_name="named_backreference_workflows.py",
                    expected_manifest_id="wrong-manifest-id",
                    expected_patterns=frozenset({r"(?P<word>ab)(?P=word)"}),
                    expected_operation_helper_counts=Counter(
                        {
                            ("compile", None): 1,
                            ("module_call", "search"): 1,
                            ("pattern_call", "search"): 1,
                        }
                    ),
                ),
            )
        )


def test_load_fixture_bundles_rejects_missing_selected_case_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "literal_flag_workflows.py is missing expected fixture rows: "
            "\\('missing-selected-case-id',\\)"
        ),
    ):
        load_fixture_bundles(
            (
                FixtureBundleSpec(
                    fixture_name="literal_flag_workflows.py",
                    expected_manifest_id="literal-flag-workflows",
                    selected_case_ids=("missing-selected-case-id",),
                    expected_patterns=frozenset(),
                    expected_operation_helper_counts=Counter(),
                ),
            )
        )


def test_fixture_bundle_contract_rejects_wrong_selected_case_order() -> None:
    (spec,) = _selected_case_bundle_specs()[:1]
    (bundle,) = load_fixture_bundles((spec,))

    with pytest.raises(AssertionError):
        assert_fixture_bundle_contract(
            bundle,
            pattern_extractor=case_pattern,
            expected_fixture_path=FIXTURES_DIR / spec.fixture_name,
            expected_ordered_case_ids=tuple(reversed(spec.selected_case_ids)),
        )


def test_selected_case_bundle_specs_load_in_declared_bundle_order() -> None:
    specs = tuple(reversed(_selected_case_bundle_specs()))

    bundles = load_fixture_bundles(specs)

    assert tuple(bundle.manifest.path.name for bundle in bundles) == tuple(
        spec.fixture_name for spec in specs
    )
    for bundle in bundles:
        assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


def test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures() -> None:
    selected_case_ids = (
        "module-sub-callable-str",
        "module-sub-grouping-template",
    )
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
                "collection_replacement_workflows.py",
                expected_manifest_id="collection-replacement-workflows",
                expected_case_ids=frozenset(selected_case_ids),
                expected_patterns=frozenset({"abc", "(abc)"}),
                expected_operation_helper_counts=Counter({("module_call", "sub"): 2}),
                selected_case_ids=selected_case_ids,
                expected_text_models=frozenset({"str"}),
            ),
        )
    )

    cases_by_id = {case.case_id: case for case in bundle.cases}

    assert bundle_patterns(bundle, pattern_extractor=case_pattern) == frozenset(
        {"abc", "(abc)"}
    )
    assert bundle_patterns(bundle, pattern_extractor=str_case_pattern) == frozenset(
        {"abc", "(abc)"}
    )
    assert set(cases_by_id) == set(selected_case_ids)
    assert cases_by_id["module-sub-callable-str"].source_args[1] == {
        "type": "callable_constant",
        "value": "x",
    }
    assert cases_by_id["module-sub-callable-str"].source_kwargs == {}
    assert cases_by_id["module-sub-grouping-template"].source_args[1] == r"\1x"
    assert cases_by_id["module-sub-grouping-template"].source_kwargs == {}


def test_ordered_manifest_cases_from_bundles_cover_manifest_order_and_unselected_rows() -> None:
    specs = _selected_case_bundle_specs()
    bundles = load_fixture_bundles(specs)

    for spec, bundle in zip(specs, bundles, strict=True):
        manifest = load_fixture_manifest(FIXTURES_DIR / spec.fixture_name)
        assert tuple(case.case_id for case in bundle.manifest.cases) == tuple(
            case.case_id for case in manifest.cases
        )

    selected_case_ids = (
        "grouped-pattern-search-single-capture-str",
        "flag-unsupported-inline-flag-search",
        "grouped-module-search-single-capture-str",
    )
    selected_cases = ordered_manifest_cases_from_bundles(
        bundles,
        selected_case_ids,
        error_label="fixture parity support contract rows",
    )

    expected_cases_by_id: dict[str, FixtureCase] = {}
    for spec in specs:
        manifest = load_fixture_manifest(FIXTURES_DIR / spec.fixture_name)
        for case in manifest.cases:
            if case.case_id in selected_case_ids:
                expected_cases_by_id[case.case_id] = case

    assert tuple(case.case_id for case in selected_cases) == selected_case_ids
    for case in selected_cases:
        expected = expected_cases_by_id[case.case_id]
        assert case.operation == expected.operation
        assert case.helper == expected.helper
        assert case.args == expected.args
        assert case.kwargs == expected.kwargs


def _grouped_match_bundle_and_uncovered_case_ids(
) -> tuple[FixtureBundleSpec, FixtureBundle, tuple[str, ...]]:
    (spec,) = _selected_case_bundle_specs()[1:]
    (bundle,) = load_fixture_bundles((spec,))
    selected_case_ids = frozenset(spec.selected_case_ids)
    uncovered_case_ids = tuple(
        case.case_id
        for case in bundle.manifest.cases
        if case.case_id not in selected_case_ids
    )
    return spec, bundle, uncovered_case_ids


def test_published_case_frontier_helper_preserves_ordered_uncovered_case_ids() -> None:
    spec, bundle, uncovered_case_ids = _grouped_match_bundle_and_uncovered_case_ids()

    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=spec.selected_case_ids,
        expected_uncovered_case_ids=uncovered_case_ids,
    )


def test_published_case_frontier_helper_rejects_duplicate_selected_case_ids() -> None:
    spec, bundle, uncovered_case_ids = _grouped_match_bundle_and_uncovered_case_ids()
    duplicated_selected_case_ids = (*spec.selected_case_ids, spec.selected_case_ids[0])

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows selected_case_ids contain duplicate ids: "
            f"{(spec.selected_case_ids[0],)}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=duplicated_selected_case_ids,
            expected_uncovered_case_ids=uncovered_case_ids,
        )


def test_published_case_frontier_helper_rejects_duplicate_uncovered_case_ids() -> None:
    spec, bundle, uncovered_case_ids = _grouped_match_bundle_and_uncovered_case_ids()
    assert uncovered_case_ids
    duplicated_uncovered_case_ids = (*uncovered_case_ids, uncovered_case_ids[0])

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows expected_uncovered_case_ids contain duplicate "
            f"ids: {(uncovered_case_ids[0],)}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=spec.selected_case_ids,
            expected_uncovered_case_ids=duplicated_uncovered_case_ids,
        )


def test_published_case_frontier_helper_rejects_selected_and_uncovered_overlap() -> None:
    spec, bundle, _ = _grouped_match_bundle_and_uncovered_case_ids()
    overlapping_case_ids = (spec.selected_case_ids[0],)

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows selected and uncovered case ids overlap: "
            f"{overlapping_case_ids}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=spec.selected_case_ids,
            expected_uncovered_case_ids=overlapping_case_ids,
        )


def test_published_case_frontier_helper_reports_missing_and_unexpected_case_ids() -> None:
    spec, bundle, uncovered_case_ids = _grouped_match_bundle_and_uncovered_case_ids()

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows published frontier drifted; "
            "missing published case ids: ('missing-case-id',); "
            f"unexpected published case ids: {uncovered_case_ids}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=spec.selected_case_ids,
            expected_uncovered_case_ids=("missing-case-id",),
        )


def test_published_case_frontier_helper_reports_uncovered_order_drift() -> None:
    spec, bundle, uncovered_case_ids = _grouped_match_bundle_and_uncovered_case_ids()
    reordered_uncovered_case_ids = tuple(reversed(uncovered_case_ids))

    assert reordered_uncovered_case_ids != uncovered_case_ids

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "grouped-match-workflows uncovered published case ids changed; "
            f"expected {reordered_uncovered_case_ids}, got {uncovered_case_ids}"
        ),
    ):
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=spec.selected_case_ids,
            expected_uncovered_case_ids=reordered_uncovered_case_ids,
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


def test_ordered_manifest_cases_from_bundles_rejects_duplicate_case_ids() -> None:
    (spec,) = _selected_case_bundle_specs()[1:]
    (bundle,) = load_fixture_bundles((spec,))

    with pytest.raises(
        AssertionError,
        match="fixture parity support contract rows contain duplicate case ids",
    ):
        ordered_manifest_cases_from_bundles(
            (bundle, bundle),
            ("grouped-module-search-single-capture-str",),
            error_label="fixture parity support contract rows",
        )


def test_ordered_manifest_cases_from_bundles_rejects_missing_case_ids() -> None:
    (spec,) = _selected_case_bundle_specs()[1:]
    (bundle,) = load_fixture_bundles((spec,))

    with pytest.raises(
        AssertionError,
        match="fixture parity support contract rows are missing case ids",
    ):
        ordered_manifest_cases_from_bundles(
            (bundle,),
            ("missing-case-id",),
            error_label="fixture parity support contract rows",
        )


def test_case_argument_helpers_cover_module_and_pattern_replacement_rows() -> None:
    module_bundle, pattern_bundle = load_fixture_bundles(
        (
            FixtureBundleSpec(
                "collection_replacement_workflows.py",
                expected_manifest_id="collection-replacement-workflows",
                expected_case_ids=frozenset({"module-sub-grouping-template"}),
                expected_patterns=frozenset({"(abc)"}),
                expected_operation_helper_counts=Counter({("module_call", "sub"): 1}),
                selected_case_ids=("module-sub-grouping-template",),
                expected_text_models=frozenset({"str"}),
            ),
            FixtureBundleSpec(
                "named_group_replacement_workflows.py",
                expected_manifest_id="named-group-replacement-workflows",
                expected_case_ids=frozenset({"pattern-sub-template-named-group-str"}),
                expected_patterns=frozenset({r"(?P<word>abc)"}),
                expected_operation_helper_counts=Counter({("pattern_call", "sub"): 1}),
                selected_case_ids=("pattern-sub-template-named-group-str",),
                expected_text_models=frozenset({"str"}),
            ),
        )
    )

    module_case = module_bundle.cases[0]
    pattern_case = pattern_bundle.cases[0]

    assert case_replacement_argument(module_case) == module_case.args[1]
    assert case_text_argument(module_case) == module_case.args[2]
    assert case_replacement_argument(pattern_case) == pattern_case.args[0]
    assert case_text_argument(pattern_case) == pattern_case.args[1]


def test_module_workflow_surface_bundle_contract_covers_verbose_compile_case() -> None:
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
                "module_workflow_surface.py",
                expected_manifest_id="module-workflow-surface",
                expected_case_ids=frozenset(
                    {
                        "workflow-compile-str-literal",
                        "workflow-compile-str-anchored-literal",
                        "workflow-compile-str-verbose-regression",
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
                        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
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
                        ("compile", None): 4,
                        ("pattern_call", "search"): 1,
                        ("pattern_call", "match"): 1,
                        ("pattern_call", "fullmatch"): 1,
                        ("cache_workflow", None): 2,
                        ("purge_workflow", None): 1,
                        ("module_call", "escape"): 2,
                    }
                ),
                expected_text_models=frozenset({"bytes", "str"}),
            ),
        )
    )

    assert bundle.manifest.path == FIXTURES_DIR / "module_workflow_surface.py"
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)
    assert "workflow-compile-str-verbose-regression" in {
        case.case_id for case in bundle.cases
    }


def test_module_workflow_surface_compile_case_selection_preserves_row_order() -> None:
    selected_case_ids = (
        "workflow-compile-str-literal",
        "workflow-compile-str-anchored-literal",
        "workflow-compile-str-verbose-regression",
        "workflow-compile-bytes-literal",
    )
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
                fixture_name="module_workflow_surface.py",
                expected_manifest_id="module-workflow-surface",
                selected_case_ids=selected_case_ids,
                expected_patterns=frozenset(
                    {
                        "abc",
                        "^abc$",
                        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
                        b"abc",
                    }
                ),
                expected_operation_helper_counts=Counter({("compile", None): 4}),
                expected_text_models=frozenset({"bytes", "str"}),
            ),
        )
    )

    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=FIXTURES_DIR / "module_workflow_surface.py",
        expected_ordered_case_ids=selected_case_ids,
    )
    assert tuple(case.case_id for case in fixture_cases_for_operation((bundle,), "compile")) == (
        selected_case_ids
    )


def test_whole_manifest_bundle_contract_supports_full_manifest_counts_without_case_ids() -> None:
    named_bundle, open_ended_bundle = load_fixture_bundles(
        (
            FixtureBundleSpec(
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
            ),
            FixtureBundleSpec(
                "open_ended_quantified_group_alternation_workflows.py",
                expected_manifest_id="open-ended-quantified-group-alternation-workflows",
                expected_patterns=frozenset(
                    {
                        r"a(bc|de){1,}d",
                        r"a(?P<word>bc|de){1,}d",
                        rb"a(bc|de){1,}d",
                        rb"a(?P<word>bc|de){1,}d",
                    }
                ),
                expected_operation_helper_counts=Counter(
                    {
                        ("compile", None): 4,
                        ("module_call", "search"): 8,
                        ("pattern_call", "fullmatch"): 20,
                    }
                ),
                expected_text_models=frozenset({"bytes", "str"}),
            ),
        )
    )

    assert open_ended_bundle.expected_case_ids is None
    assert_fixture_bundle_contract(
        open_ended_bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=(
            FIXTURES_DIR / "open_ended_quantified_group_alternation_workflows.py"
        ),
    )
    assert tuple(
        path.name
        for path in published_fixture_paths_from_bundles((open_ended_bundle, named_bundle))
    ) == (
        "named_backreference_workflows.py",
        "open_ended_quantified_group_alternation_workflows.py",
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
