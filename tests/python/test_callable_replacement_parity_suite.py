from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import (
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
    CpythonReAdapter,
    FixtureCase,
    RebarAdapter,
    evaluate_case,
    normalize_exception,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    bundle_patterns,
    case_replacement_argument,
    case_text_argument,
    load_fixture_bundles,
    load_published_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
    str_case_pattern,
)


COLLECTION_REPLACEMENT_FIXTURE_NAME = "collection_replacement_workflows.py"

@dataclass(frozen=True)
class CallableManifestSpec:
    manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    has_near_miss_matrix: bool


@dataclass(frozen=True)
class CallableNearMissCase:
    id: str
    manifest_id: str
    use_compiled_pattern: bool
    pattern: str
    helper: str
    text: str
    count: int
    expected_result: str | tuple[str, int]


CALLABLE_MANIFEST_SPECS = (
    CallableManifestSpec(
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-quantified-nested-group-alternation-numbered-lower-bound-b-branch-str",
                "module-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-c-branch-str",
                "pattern-sub-callable-quantified-nested-group-alternation-numbered-mixed-branches-str",
                "pattern-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-b-branch-str",
                "module-sub-callable-quantified-nested-group-alternation-named-lower-bound-c-branch-str",
                "module-subn-callable-quantified-nested-group-alternation-named-first-match-only-b-branch-str",
                "pattern-sub-callable-quantified-nested-group-alternation-named-mixed-branches-str",
                "pattern-subn-callable-quantified-nested-group-alternation-named-first-match-only-c-branch-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c)+)d",
                r"a(?P<outer>(?P<inner>b|c)+)d",
            }
        ),
        has_near_miss_matrix=True,
    ),
    CallableManifestSpec(
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-callable-conditional-group-exists-present-str",
                "module-subn-callable-conditional-group-exists-absent-str",
                "pattern-sub-callable-conditional-group-exists-present-str",
                "pattern-subn-callable-conditional-group-exists-absent-str",
                "module-sub-callable-named-conditional-group-exists-present-str",
                "module-subn-callable-named-conditional-group-exists-absent-str",
                "pattern-sub-callable-named-conditional-group-exists-present-str",
                "pattern-subn-callable-named-conditional-group-exists-absent-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        has_near_miss_matrix=True,
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){2,})\2d",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
            }
        ),
        has_near_miss_matrix=True,
    ),
    CallableManifestSpec(
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
                "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
                "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
                "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){2,})\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            }
        ),
        has_near_miss_matrix=False,
    ),
)
CALLABLE_MANIFEST_PARAMS = tuple(
    pytest.param(spec, id=spec.manifest_id) for spec in CALLABLE_MANIFEST_SPECS
)
CALLABLE_NEAR_MISS_CASE_SPECS = (
    CallableNearMissCase(
        id="module-numbered-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(b)?c(?(1)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-present-branch-rejects-no-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="sub",
        text="zzabcezz",
        count=0,
        expected_result="zzabcezz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-absent-branch-rejects-yes-arm",
        manifest_id="conditional-group-exists-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        helper="subn",
        text="zzacdzz",
        count=1,
        expected_result=("zzacdzz", 0),
    ),
    CallableNearMissCase(
        id="module-numbered-sub-no-match-too-short",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a((b|c)+)d",
        helper="sub",
        text="zzadzz",
        count=0,
        expected_result="zzadzz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-invalid-branch",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=False,
        pattern=r"a((b|c)+)d",
        helper="subn",
        text="zzabedzz",
        count=0,
        expected_result=("zzabedzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-too-short",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c)+)d",
        helper="sub",
        text="zzadzz",
        count=0,
        expected_result="zzadzz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-invalid-branch",
        manifest_id="quantified-nested-group-alternation-callable-replacement-workflows",
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c)+)d",
        helper="subn",
        text="zzabedzz",
        count=0,
        expected_result=("zzabedzz", 0),
    ),
    CallableNearMissCase(
        id="module-numbered-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a((b|c){2,})\2d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-numbered-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a((b|c){2,})\2d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-numbered-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a((b|c){2,})\2d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-numbered-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a((b|c){2,})\2d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="module-named-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="module-named-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=False,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
    CallableNearMissCase(
        id="pattern-named-sub-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="sub",
        text="zzabbdzz",
        count=0,
        expected_result="zzabbdzz",
    ),
    CallableNearMissCase(
        id="pattern-named-subn-no-match-missing-replay-broader-range",
        manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows"
        ),
        use_compiled_pattern=True,
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        helper="subn",
        text="zzabbdzz",
        count=1,
        expected_result=("zzabbdzz", 0),
    ),
)
CALLABLE_NEAR_MISS_CASES = tuple(
    pytest.param(case, id=case.id) for case in CALLABLE_NEAR_MISS_CASE_SPECS
)
CALLABLE_NEAR_MISS_MANIFEST_IDS = frozenset(
    case.manifest_id for case in CALLABLE_NEAR_MISS_CASE_SPECS
)


class CallbackExplosion(RuntimeError):
    pass


def _assert_callback_match_sequence_parity(
    *,
    backend_name: str,
    observed_matches: list[object],
    expected_matches: list[re.Match[str]],
) -> None:
    assert len(observed_matches) == len(expected_matches)

    for observed, expected in zip(observed_matches, expected_matches, strict=True):
        assert_match_parity(
            backend_name,
            observed,
            expected,
            check_regs=True,
        )
        assert_match_convenience_api_parity(observed, expected)
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)


def assert_callable_replacement_match_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: str,
    string: str,
    count: int,
    group_names: tuple[str, ...] = (),
    use_compiled_pattern: bool = False,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str]] = []

    def observed_replacement(match: object) -> str:
        observed_matches.append(match)
        return "X"

    def expected_replacement(match: re.Match[str]) -> str:
        expected_matches.append(match)
        return "X"

    if use_compiled_pattern:
        observed_target = backend.compile(pattern)
        expected_target = re.compile(pattern)
        observed = getattr(observed_target, helper)(
            observed_replacement,
            string,
            count=count,
        )
        expected = getattr(expected_target, helper)(
            expected_replacement,
            string,
            count=count,
        )
    else:
        observed = getattr(backend, helper)(
            pattern,
            observed_replacement,
            string,
            count=count,
        )
        expected = getattr(re, helper)(
            pattern,
            expected_replacement,
            string,
            count=count,
        )

    assert observed == expected
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )


def assert_callable_replacement_exception_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: str,
    string: str,
    count: int,
    group_names: tuple[str, ...] = (),
    use_compiled_pattern: bool = False,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str]] = []
    marker_message = "callable replacement callback exploded"
    observed_marker = CallbackExplosion(marker_message)
    expected_marker = CallbackExplosion(marker_message)

    def observed_replacement(match: object) -> str:
        observed_matches.append(match)
        raise observed_marker

    def expected_replacement(match: re.Match[str]) -> str:
        expected_matches.append(match)
        raise expected_marker

    with pytest.raises(CallbackExplosion) as observed_error:
        if use_compiled_pattern:
            observed_target = backend.compile(pattern)
            getattr(observed_target, helper)(
                observed_replacement,
                string,
                count=count,
            )
        else:
            getattr(backend, helper)(
                pattern,
                observed_replacement,
                string,
                count=count,
            )

    with pytest.raises(CallbackExplosion) as expected_error:
        if use_compiled_pattern:
            expected_target = re.compile(pattern)
            getattr(expected_target, helper)(
                expected_replacement,
                string,
                count=count,
            )
        else:
            getattr(re, helper)(
                pattern,
                expected_replacement,
                string,
                count=count,
            )

    assert observed_error.value is observed_marker
    assert expected_error.value is expected_marker
    assert observed_error.value.args == expected_error.value.args == (marker_message,)
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )
    assert len(observed_matches) == 1


def assert_pattern_callable_replacement_return_type_error_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: str,
    string: str,
    count: int,
) -> None:
    observed_matches: list[object] = []
    expected_matches: list[re.Match[str]] = []

    def observed_replacement(match: object) -> bytes:
        observed_matches.append(match)
        return b"X"

    def expected_replacement(match: re.Match[str]) -> bytes:
        expected_matches.append(match)
        return b"X"

    expected_target = re.compile(pattern)
    with pytest.raises(TypeError) as expected_error:
        getattr(expected_target, helper)(
            expected_replacement,
            string,
            count=count,
        )

    observed_target = backend.compile(pattern)
    with pytest.raises(TypeError) as observed_error:
        getattr(observed_target, helper)(
            observed_replacement,
            string,
            count=count,
        )

    assert observed_error.value.args == expected_error.value.args
    _assert_callback_match_sequence_parity(
        backend_name=backend_name,
        observed_matches=observed_matches,
        expected_matches=expected_matches,
    )


CALLABLE_FIXTURE_PATHS = select_correctness_fixture_paths(
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR
)
LITERAL_CALLABLE_PARITY_VARIANTS = (
    pytest.param("sub", 0, False, id="literal-module-sub-replace-all"),
    pytest.param("subn", 1, False, id="literal-module-subn-first-match-only"),
    pytest.param("sub", 0, True, id="literal-pattern-sub-replace-all"),
    pytest.param("subn", 1, True, id="literal-pattern-subn-first-match-only"),
)
CALLABLE_NO_MATCH_VARIANTS = (
    pytest.param("sub", False, id="module-sub"),
    pytest.param("subn", False, id="module-subn"),
    pytest.param("sub", True, id="pattern-sub"),
    pytest.param("subn", True, id="pattern-subn"),
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
PENDING_REBAR_MANIFEST_IDS = frozenset()
NO_MATCH_TEXT_CANDIDATES = ("zzz", "", "no-match", "----", "999")


def _skip_pending_rebar_callable_parity(
    backend_name: str,
    case: FixtureCase,
) -> None:
    if (
        backend_name == "rebar"
        and case.manifest_id in PENDING_REBAR_MANIFEST_IDS
    ):
        pytest.skip(
            f"callable replacement parity for {case.manifest_id} remains queued behind a later Rust-backed parity task"
        )


def _pending_rebar_compile_patterns() -> frozenset[str]:
    return frozenset(
        compile_pattern
        for bundle in FIXTURE_BUNDLES
        if bundle.manifest.manifest_id in PENDING_REBAR_MANIFEST_IDS
        for compile_pattern in bundle_patterns(
            bundle,
            pattern_extractor=str_case_pattern,
        )
    )

COLLECTION_REPLACEMENT_BUNDLE, = load_fixture_bundles(
    (
        FixtureBundleSpec(
            COLLECTION_REPLACEMENT_FIXTURE_NAME,
            expected_manifest_id="collection-replacement-workflows",
            selected_case_ids=("module-sub-callable-str",),
            expected_patterns=frozenset({"abc"}),
            expected_operation_helper_counts=Counter({("module_call", "sub"): 1}),
            expected_text_models=frozenset({"str"}),
        ),
    )
)
FIXTURE_BUNDLES = load_published_fixture_bundles(CALLABLE_FIXTURE_PATHS)

COMPILE_PATTERNS = tuple(
    sorted(
        {
            compile_pattern
            for bundle in FIXTURE_BUNDLES
            for compile_pattern in bundle_patterns(
                bundle,
                pattern_extractor=str_case_pattern,
            )
        }
    )
)
MODULE_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "pattern_call"
)
CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS = (
    "quantified",
    "broader-range",
    "open-ended",
)
PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS = frozenset(
    {
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
        "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows",
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
        "nested-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
        "quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows",
        "quantified-nested-group-alternation-callable-replacement-workflows",
        "quantified-nested-group-callable-replacement-workflows",
    }
)
PATTERN_RETURN_TYPE_ERROR_CASES = tuple(
    case
    for case in PATTERN_CASES
    if any(
        keyword in case.manifest_id
        for keyword in CALLABLE_RETURN_TYPE_ERROR_MANIFEST_KEYWORDS
    )
)


def _literal_callable_case() -> FixtureCase:
    return COLLECTION_REPLACEMENT_BUNDLE.cases[0]


def _source_callable_replacement(case: FixtureCase) -> dict[str, object]:
    replacement_index = 1 if case.operation == "module_call" else 0
    replacement = case.source_args[replacement_index]
    assert isinstance(replacement, dict)
    return replacement


def _literal_callable_pattern() -> str:
    pattern = _literal_callable_case().args[0]
    assert isinstance(pattern, str)
    return pattern


def _literal_callable_string() -> str:
    string = _literal_callable_case().args[2]
    assert isinstance(string, str)
    return string


def _case_string(case: FixtureCase) -> str:
    string = case_text_argument(case)
    assert isinstance(string, str)
    return string


def _case_count(case: FixtureCase) -> int:
    if "count" in case.kwargs:
        return int(case.kwargs["count"])

    count_index = 3 if case.operation == "module_call" else 2
    if len(case.args) > count_index:
        return int(case.args[count_index])
    return 0


def _case_group_names(case: FixtureCase) -> tuple[str, ...]:
    return tuple(re.compile(str_case_pattern(case), case.flags or 0).groupindex)


def _invoke_callable_replacement(
    backend: object,
    *,
    pattern: str,
    helper: str,
    string: str,
    count: int,
    replacement: object,
    use_compiled_pattern: bool,
) -> object:
    if use_compiled_pattern:
        target = backend.compile(pattern)
        return getattr(target, helper)(replacement, string, count=count)

    return getattr(backend, helper)(pattern, replacement, string, count=count)


def _invoke_published_callable_case(backend: object, case: FixtureCase) -> object:
    if case.helper is None:
        raise ValueError(f"case {case.case_id!r} requires a helper name")

    if case.operation == "module_call":
        return getattr(backend, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        compiled = backend.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise ValueError(f"unsupported callable replacement operation {case.operation!r}")


def _observe_published_callable_case(backend: object, case: FixtureCase) -> tuple[str, object]:
    try:
        return ("result", _invoke_published_callable_case(backend, case))
    except Exception as exc:
        return ("exception", normalize_exception(exc))


def _callable_no_match_text(pattern: str, flags: int = 0) -> str:
    compiled = re.compile(pattern, flags)
    for text in NO_MATCH_TEXT_CANDIDATES:
        if compiled.search(text) is None:
            return text

    raise AssertionError(f"could not find a shared no-match text for pattern {pattern!r}")


def assert_callable_replacement_negative_count_short_circuits(
    *,
    backend: object,
    helper: str,
    pattern: str,
    string: str,
    use_compiled_pattern: bool = False,
) -> None:
    callback_calls: list[object] = []

    def replacement(match: object) -> str:
        callback_calls.append(match)
        return "X"

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper=helper,
        string=string,
        count=-1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper=helper,
        string=string,
        count=-1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected_result: object = string if helper == "sub" else (string, 0)

    assert observed == expected == expected_result
    assert callback_calls == []


def assert_callable_replacement_invalid_count_typeerror_parity(
    *,
    backend: object,
    helper: str,
    pattern: str,
    string: str,
    count: object,
    use_compiled_pattern: bool = False,
) -> None:
    callback_calls: list[object] = []

    def replacement(match: object) -> str:
        callback_calls.append(match)
        return "X"

    with pytest.raises(TypeError) as observed_error:
        _invoke_callable_replacement(
            backend,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    with pytest.raises(TypeError) as expected_error:
        _invoke_callable_replacement(
            re,
            pattern=pattern,
            helper=helper,
            string=string,
            count=count,
            replacement=replacement,
            use_compiled_pattern=use_compiled_pattern,
        )

    assert type(observed_error.value) is type(expected_error.value)
    assert observed_error.value.args == expected_error.value.args
    assert callback_calls == []


def _assert_source_callable_replacement_reference_is_valid(case: FixtureCase) -> None:
    replacement = _source_callable_replacement(case)
    assert replacement.get("type") == "callable_match_group"

    prefix = replacement.get("prefix", "")
    suffix = replacement.get("suffix", "")
    assert isinstance(prefix, str)
    assert isinstance(suffix, str)

    compiled = re.compile(str_case_pattern(case), case.flags or 0)
    group_reference = replacement.get("group", 0)
    if isinstance(group_reference, int):
        assert 0 <= group_reference <= compiled.groups
    else:
        assert isinstance(group_reference, str)
        assert group_reference in compiled.groupindex


def _live_unimplemented_callable_manifest_ids() -> frozenset[str]:
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()
    manifest_ids: set[str] = set()

    for bundle in FIXTURE_BUNDLES:
        for case in bundle.cases:
            evaluation = evaluate_case(case, cpython_adapter, rebar_adapter)
            if evaluation["comparison"] == "unimplemented":
                manifest_ids.add(case.manifest_id)

    return frozenset(manifest_ids)
def test_pending_rebar_callable_manifest_ids_match_live_unimplemented_manifests() -> None:
    assert _live_unimplemented_callable_manifest_ids() == PENDING_REBAR_MANIFEST_IDS


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.manifest.manifest_id,
)
def test_callable_replacement_fixture_shape_contract(
    bundle: FixtureBundle,
) -> None:
    compile_patterns = bundle_patterns(bundle, pattern_extractor=str_case_pattern)

    assert bundle.manifest.manifest_id.endswith("-callable-replacement-workflows")
    assert bundle.manifest.layer == "module_workflow"
    assert bundle.manifest.defaults.get("text_model") == "str"
    assert len(bundle.cases) == 8
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )
    assert len(compile_patterns) == 2

    has_named_pattern = False
    has_numbered_pattern = False
    for pattern in compile_patterns:
        compiled = re.compile(pattern)
        if compiled.groupindex:
            has_named_pattern = True
        else:
            has_numbered_pattern = True

    assert has_named_pattern
    assert has_numbered_pattern

    for case in bundle.cases:
        assert "callable-replacement" in case.categories
        assert "str" in case.categories
        _assert_source_callable_replacement_reference_is_valid(case)


def test_literal_callable_case_stays_aligned_with_published_collection_fixture() -> None:
    case = _literal_callable_case()
    source_replacement = _source_callable_replacement(case)

    assert COLLECTION_REPLACEMENT_BUNDLE.manifest.manifest_id == (
        "collection-replacement-workflows"
    )
    assert case.operation == "module_call"
    assert case.helper == "sub"
    assert _literal_callable_pattern() == "abc"
    assert _literal_callable_string() == "abcabc"
    assert callable(case_replacement_argument(case))
    assert "callable-replacement" in case.categories
    assert "str" in case.categories
    assert source_replacement == {"type": "callable_constant", "value": "x"}
    assert case.source_kwargs == {}


@pytest.mark.parametrize("manifest_spec", CALLABLE_MANIFEST_PARAMS)
def test_callable_replacement_cases_stay_aligned_with_published_fixture(
    manifest_spec: CallableManifestSpec,
) -> None:
    bundle = published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        manifest_spec.manifest_id,
    )

    assert bundle.manifest.manifest_id == manifest_spec.manifest_id
    assert len(bundle.cases) == len(manifest_spec.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == manifest_spec.expected_case_ids
    assert bundle_patterns(bundle, pattern_extractor=str_case_pattern) == (
        manifest_spec.expected_compile_patterns
    )
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )
    assert manifest_spec.has_near_miss_matrix is (
        manifest_spec.manifest_id in CALLABLE_NEAR_MISS_MANIFEST_IDS
    )


def test_pattern_callable_replacement_return_type_error_cases_cover_quantified_callable_fixture_frontier(
) -> None:
    assert PATTERN_RETURN_TYPE_ERROR_CASES
    assert {
        case.manifest_id for case in PATTERN_RETURN_TYPE_ERROR_CASES
    } == PATTERN_RETURN_TYPE_ERROR_EXPECTED_MANIFEST_IDS


NO_MATCH_PATTERNS = tuple(sorted({*COMPILE_PATTERNS, _literal_callable_pattern()}))
PENDING_REBAR_COMPILE_PATTERNS = _pending_rebar_compile_patterns()
PENDING_REBAR_NO_MATCH_PATTERNS = PENDING_REBAR_COMPILE_PATTERNS


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend

    if backend_name == "rebar" and pattern in PENDING_REBAR_COMPILE_PATTERNS:
        pytest.skip(
            f"callable replacement parity for pattern {pattern!r} remains queued behind a later Rust-backed parity task"
        )

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    LITERAL_CALLABLE_PARITY_VARIANTS,
)
def test_literal_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    def replacement(_match: object) -> str:
        return "x"

    if use_compiled_pattern:
        observed_target = backend.compile(_literal_callable_pattern())
        expected_target = re.compile(_literal_callable_pattern())
        observed = getattr(observed_target, helper)(
            replacement,
            _literal_callable_string(),
            count=count,
        )
        expected = getattr(expected_target, helper)(
            replacement,
            _literal_callable_string(),
            count=count,
        )
    else:
        observed = getattr(backend, helper)(
            _literal_callable_pattern(),
            replacement,
            _literal_callable_string(),
            count=count,
        )
        expected = getattr(re, helper)(
            _literal_callable_pattern(),
            replacement,
            _literal_callable_string(),
            count=count,
        )

    assert observed == expected


@pytest.mark.parametrize("pattern", NO_MATCH_PATTERNS)
@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_callable_replacement_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    pattern: str,
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    if backend_name == "rebar" and pattern in PENDING_REBAR_NO_MATCH_PATTERNS:
        pytest.skip(
            f"callable replacement parity for pattern {pattern!r} remains queued behind a later Rust-backed parity task"
        )

    callback_calls: list[object] = []
    string = _callable_no_match_text(pattern)

    def replacement(match: object) -> str:
        callback_calls.append(match)
        return "X"

    observed = _invoke_callable_replacement(
        backend,
        pattern=pattern,
        helper=helper,
        string=string,
        count=1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=pattern,
        helper=helper,
        string=string,
        count=1,
        replacement=replacement,
        use_compiled_pattern=use_compiled_pattern,
    )
    expected_result: object = string if helper == "sub" else (string, 0)

    assert observed == expected == expected_result
    assert callback_calls == []


@pytest.mark.parametrize("near_miss_case", CALLABLE_NEAR_MISS_CASES)
def test_callable_replacement_near_miss_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    near_miss_case: CallableNearMissCase,
) -> None:
    backend_name, backend = regex_backend
    if (
        backend_name == "rebar"
        and near_miss_case.pattern in PENDING_REBAR_NO_MATCH_PATTERNS
    ):
        pytest.skip(
            f"callable replacement parity for pattern {near_miss_case.pattern!r} remains queued behind a later Rust-backed parity task"
        )

    callback_calls: list[object] = []

    def replacement(match: object) -> str:
        callback_calls.append(match)
        return "X"

    observed = _invoke_callable_replacement(
        backend,
        pattern=near_miss_case.pattern,
        helper=near_miss_case.helper,
        string=near_miss_case.text,
        count=near_miss_case.count,
        replacement=replacement,
        use_compiled_pattern=near_miss_case.use_compiled_pattern,
    )
    expected = _invoke_callable_replacement(
        re,
        pattern=near_miss_case.pattern,
        helper=near_miss_case.helper,
        string=near_miss_case.text,
        count=near_miss_case.count,
        replacement=replacement,
        use_compiled_pattern=near_miss_case.use_compiled_pattern,
    )

    assert observed == expected == near_miss_case.expected_result
    assert callback_calls == []


@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_literal_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_negative_count_short_circuits_without_callback(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_negative_count_short_circuits(
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize(
    ("helper", "use_compiled_pattern"),
    CALLABLE_NO_MATCH_VARIANTS,
)
def test_literal_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    helper: str,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend

    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        count=None,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=None,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_none_count_matches_cpython_typeerror(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_invalid_count_typeerror_parity(
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=None,
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    observed = _observe_published_callable_case(backend, case)
    expected = _observe_published_callable_case(re, case)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    observed = _observe_published_callable_case(backend, case)
    expected = _observe_published_callable_case(re, case)

    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    LITERAL_CALLABLE_PARITY_VARIANTS,
)
def test_literal_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    LITERAL_CALLABLE_PARITY_VARIANTS,
)
def test_literal_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend

    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=_literal_callable_pattern(),
        string=_literal_callable_string(),
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_callback_exception_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_callable_replacement_exception_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=True,
    )


@pytest.mark.parametrize(
    "case",
    PATTERN_RETURN_TYPE_ERROR_CASES,
    ids=lambda case: case.case_id,
)
def test_pattern_callable_replacement_wrong_return_type_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    _skip_pending_rebar_callable_parity(backend_name, case)
    assert_pattern_callable_replacement_return_type_error_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=str_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
    )
