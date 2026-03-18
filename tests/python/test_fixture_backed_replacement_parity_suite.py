from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
import pathlib
import re

import pytest

from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_convenience_api_parity,
    assert_match_parity,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    fixture_cases_from_bundles,
    load_fixture_bundles,
    published_fixture_paths_from_bundles,
    str_case_pattern,
)

TextValue = str | bytes
ReplacementOutcome = TextValue | tuple[TextValue, int]

EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 4,
        ("module_call", "subn"): 4,
        ("pattern_call", "sub"): 4,
        ("pattern_call", "subn"): 4,
    }
)
MIXED_TEXT_MODELS = frozenset({"bytes", "str"})
NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID = (
    "nested-broader-range-open-ended-quantified-group-alternation-"
    "branch-local-backreference-conditional-replacement-workflows"
)
KNOWN_UNCOVERED_PUBLISHED_FIXTURE_FILENAMES: tuple[str, ...] = ()
NO_MATCH_TEXT_CANDIDATES = (
    "zzz",
    "",
    "----",
    "no-match",
    "999",
    "ffff",
    "ac",
    "ae",
    "ad",
)
CONDITIONAL_REPLACEMENT_SELECTOR_FIXTURE_PATHS = select_correctness_fixture_paths(
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR
)


@dataclass(frozen=True)
class SupplementalReplacementCase:
    id: str
    use_compiled_pattern: bool
    helper: str
    pattern: TextValue
    replacement: TextValue
    string: TextValue
    count: int | None = None
    expected_result: ReplacementOutcome | None = None


@dataclass(frozen=True)
class ReplacementSurfaceSpec:
    id: str
    bundle_specs: tuple[FixtureBundleSpec, ...]
    pattern_extractor: Callable[[FixtureCase], TextValue]
    compile_patterns: tuple[TextValue, ...] = ()
    match_snapshot_manifest_ids: tuple[str, ...] = ()
    template_expand_manifest_ids: tuple[str, ...] = ()
    selector_fixture_paths: tuple[pathlib.Path, ...] = ()
    known_uncovered_published_fixture_filenames: tuple[str, ...] = ()
    discover_no_match_on_all_replacement_cases: bool = False
    no_match_text_candidates: tuple[TextValue, ...] = ()
    supplemental_no_match_cases: tuple[SupplementalReplacementCase, ...] = ()
    supplemental_repeated_cases: tuple[SupplementalReplacementCase, ...] = ()
    pending_bytes_follow_on_manifest_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class LoadedReplacementSurface:
    spec: ReplacementSurfaceSpec
    bundles: tuple[FixtureBundle, ...]
    replacement_cases: tuple[FixtureCase, ...]
    module_cases: tuple[FixtureCase, ...]
    pattern_cases: tuple[FixtureCase, ...]
    match_snapshot_cases: tuple[FixtureCase, ...]
    template_expand_cases: tuple[FixtureCase, ...]
    discovered_no_match_cases: tuple[FixtureCase, ...]


OPEN_ENDED_SUPPLEMENTAL_NO_MATCH_CASES = (
    SupplementalReplacementCase(
        id="module-open-ended-numbered-sub-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a((b|c){1,})\2d",
        replacement=r"\1x",
        string="zzabdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="module-open-ended-numbered-subn-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a((b|c){1,})\2d",
        replacement=r"\2x",
        string="zzabdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-open-ended-numbered-sub-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a((b|c){1,})\2d",
        replacement=r"\1x",
        string="zzabdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="pattern-open-ended-numbered-subn-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a((b|c){1,})\2d",
        replacement=r"\2x",
        string="zzabdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="module-open-ended-named-sub-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        replacement=r"\g<outer>x",
        string="zzabdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="module-open-ended-named-subn-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        replacement=r"\g<inner>x",
        string="zzabdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-open-ended-named-sub-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        replacement=r"\g<outer>x",
        string="zzabdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="pattern-open-ended-named-subn-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        replacement=r"\g<inner>x",
        string="zzabdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="module-broader-range-numbered-sub-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a((b|c){2,})\2d",
        replacement=r"\1x",
        string="zzabbdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="module-broader-range-numbered-subn-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a((b|c){2,})\2d",
        replacement=r"\2x",
        string="zzabbdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-broader-range-numbered-sub-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a((b|c){2,})\2d",
        replacement=r"\1x",
        string="zzabbdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="pattern-broader-range-numbered-subn-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a((b|c){2,})\2d",
        replacement=r"\2x",
        string="zzabbdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="module-broader-range-named-sub-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        replacement=r"\g<outer>x",
        string="zzabbdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="module-broader-range-named-subn-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        replacement=r"\g<inner>x",
        string="zzabbdzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-broader-range-named-sub-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        replacement=r"\g<outer>x",
        string="zzabbdzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="pattern-broader-range-named-subn-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        replacement=r"\g<inner>x",
        string="zzabbdzz",
        count=1,
    ),
)

OPEN_ENDED_SUPPLEMENTAL_REPEATED_CASES = (
    SupplementalReplacementCase(
        id="module-open-ended-numbered-sub-repeated-matches",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a((b|c){1,})\2d",
        replacement=r"\1x",
        string="abbdabcbccd",
        expected_result="bxbcbcx",
    ),
    SupplementalReplacementCase(
        id="pattern-open-ended-named-sub-repeated-matches",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        replacement=r"\g<outer>x",
        string="abbdabcbccd",
        expected_result="bxbcbcx",
    ),
    SupplementalReplacementCase(
        id="module-open-ended-named-subn-repeated-matches",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        replacement=r"\g<inner>x",
        string="abbdabcbccd",
        expected_result=("bxcx", 2),
    ),
    SupplementalReplacementCase(
        id="pattern-open-ended-numbered-subn-repeated-matches",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a((b|c){1,})\2d",
        replacement=r"\2x",
        string="abbdabcbccd",
        expected_result=("bxcx", 2),
    ),
    SupplementalReplacementCase(
        id="module-broader-range-numbered-sub-repeated-matches",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a((b|c){2,})\2d",
        replacement=r"\1x",
        string="abbbdabcbccd",
        expected_result="bbxbcbcx",
    ),
    SupplementalReplacementCase(
        id="pattern-broader-range-named-sub-repeated-matches",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        replacement=r"\g<outer>x",
        string="abbbdabcbccd",
        expected_result="bbxbcbcx",
    ),
    SupplementalReplacementCase(
        id="module-broader-range-named-subn-repeated-matches",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        replacement=r"\g<inner>x",
        string="abbbdabcbccd",
        expected_result=("bxcx", 2),
    ),
    SupplementalReplacementCase(
        id="pattern-broader-range-numbered-subn-repeated-matches",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a((b|c){2,})\2d",
        replacement=r"\2x",
        string="abbbdabcbccd",
        expected_result=("bxcx", 2),
    ),
)

CONDITIONAL_SUPPLEMENTAL_REPEATED_CASES = (
    SupplementalReplacementCase(
        id="module-numbered-sub-repeated-template-present-absent-present",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a(b)?c(?(1)d|e)",
        replacement=r"\1x",
        string="abcdaceabcd",
        count=0,
        expected_result="bxxbx",
    ),
    SupplementalReplacementCase(
        id="module-named-subn-template-first-match-mixed-captures",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        replacement=r"\g<word>x",
        string="abcdaceabcd",
        count=1,
        expected_result=("bxaceabcd", 1),
    ),
    SupplementalReplacementCase(
        id="pattern-named-sub-repeated-template-present-absent-present",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        replacement=r"\g<word>x",
        string="abcdaceabcd",
        count=0,
        expected_result="bxxbx",
    ),
    SupplementalReplacementCase(
        id="pattern-numbered-subn-template-first-match-mixed-captures",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a(b)?c(?(1)d|e)",
        replacement=r"\1x",
        string="abcdaceabcd",
        count=1,
        expected_result=("bxaceabcd", 1),
    ),
)


def _pattern_from_extractor(
    pattern_extractor: Callable[[FixtureCase], TextValue],
    case: FixtureCase,
) -> TextValue:
    pattern = pattern_extractor(case)
    assert isinstance(pattern, (str, bytes))
    return pattern


def _pattern_sort_key(pattern: TextValue) -> tuple[int, TextValue]:
    if isinstance(pattern, str):
        return (0, pattern)
    return (1, pattern)


def _sorted_compile_patterns(
    cases: tuple[FixtureCase, ...],
    *,
    pattern_extractor: Callable[[FixtureCase], TextValue],
) -> tuple[TextValue, ...]:
    return tuple(
        sorted(
            {_pattern_from_extractor(pattern_extractor, case) for case in cases},
            key=_pattern_sort_key,
        )
    )


def _pattern_param_id(pattern: TextValue) -> str:
    if isinstance(pattern, bytes):
        return repr(pattern)
    return pattern


def _cases_for_manifest_ids(
    cases: tuple[FixtureCase, ...],
    manifest_ids: tuple[str, ...],
) -> tuple[FixtureCase, ...]:
    if not manifest_ids:
        return ()

    duplicate_manifest_ids = tuple(
        manifest_id
        for manifest_id, count in Counter(manifest_ids).items()
        if count > 1
    )
    if duplicate_manifest_ids:
        raise ValueError(
            f"duplicate manifest ids in case partition: {duplicate_manifest_ids}"
        )

    available_manifest_ids = frozenset(case.manifest_id for case in cases)
    missing_manifest_ids = tuple(
        manifest_id for manifest_id in manifest_ids if manifest_id not in available_manifest_ids
    )
    if missing_manifest_ids:
        raise ValueError(
            f"unknown manifest ids in case partition: {missing_manifest_ids}"
        )

    return tuple(
        case
        for manifest_id in manifest_ids
        for case in cases
        if case.manifest_id == manifest_id
    )


def _load_surface(spec: ReplacementSurfaceSpec) -> LoadedReplacementSurface:
    bundles = load_fixture_bundles(spec.bundle_specs)
    published_replacement_cases = fixture_cases_from_bundles(bundles)
    replacement_cases = tuple(
        case
        for case in published_replacement_cases
        if case.text_model != "bytes"
        or case.manifest_id not in spec.pending_bytes_follow_on_manifest_ids
    )
    compile_patterns = _sorted_compile_patterns(
        replacement_cases,
        pattern_extractor=spec.pattern_extractor,
    )
    if spec.compile_patterns and compile_patterns != spec.compile_patterns:
        raise ValueError(
            f"{spec.id} compile patterns drifted: {compile_patterns!r} != {spec.compile_patterns!r}"
        )

    return LoadedReplacementSurface(
        spec=spec,
        bundles=bundles,
        replacement_cases=replacement_cases,
        module_cases=tuple(
            case for case in replacement_cases if case.operation == "module_call"
        ),
        pattern_cases=tuple(
            case for case in replacement_cases if case.operation == "pattern_call"
        ),
        match_snapshot_cases=_cases_for_manifest_ids(
            replacement_cases,
            spec.match_snapshot_manifest_ids,
        ),
        template_expand_cases=_cases_for_manifest_ids(
            replacement_cases,
            spec.template_expand_manifest_ids,
        ),
        discovered_no_match_cases=(
            replacement_cases if spec.discover_no_match_on_all_replacement_cases else ()
        ),
    )


def _replacement_args(
    case: FixtureCase,
    *,
    text: TextValue | None = None,
) -> tuple[object, ...]:
    args = list(case.args)
    if text is None:
        return tuple(args)

    text_index = 2 if case.operation == "module_call" else 1
    args[text_index] = text
    return tuple(args)


def _invoke_helper(
    target: object,
    helper: str,
    *args: object,
    count: int | None,
) -> object:
    if count is None:
        return getattr(target, helper)(*args)
    return getattr(target, helper)(*args, count=count)


def _run_replacement_case(
    backend: object,
    case: FixtureCase,
    *,
    text: TextValue | None = None,
) -> object:
    if case.helper is None:
        raise ValueError(f"case {case.case_id!r} requires a helper name")

    if case.operation == "module_call":
        return getattr(backend, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    if case.operation == "pattern_call":
        compiled = backend.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(
            *_replacement_args(case, text=text),
            **case.kwargs,
        )

    raise ValueError(f"unsupported replacement parity operation {case.operation!r}")


def _search_match_for_case(
    surface: LoadedReplacementSurface,
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str] | re.Match[bytes]]:
    pattern = _pattern_from_extractor(surface.spec.pattern_extractor, case)
    string = case_text_argument(case)

    if case.operation == "module_call":
        observed = backend.search(pattern, string, case.flags or 0)
        expected = re.search(pattern, string, case.flags or 0)
    elif case.operation == "pattern_call":
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
            case.flags or 0,
        )
        observed = observed_pattern.search(string)
        expected = expected_pattern.search(string)
    else:
        raise ValueError(f"unsupported replacement parity operation {case.operation!r}")

    assert observed is not None
    assert expected is not None
    return observed, expected


def _no_match_text(
    surface: LoadedReplacementSurface,
    case: FixtureCase,
) -> TextValue:
    compiled = re.compile(
        _pattern_from_extractor(surface.spec.pattern_extractor, case),
        case.flags or 0,
    )
    case_text = case_text_argument(case)
    for text in surface.spec.no_match_text_candidates:
        if isinstance(case_text, str) != isinstance(text, str):
            continue
        if compiled.search(text) is None:
            return text

    raise AssertionError(f"could not find a shared no-match text for {case.case_id!r}")


def _run_supplemental_replacement_case(
    backend_name: str,
    backend: object,
    case: SupplementalReplacementCase,
) -> tuple[object, object]:
    if case.use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
        )
        observed = _invoke_helper(
            observed_pattern,
            case.helper,
            case.replacement,
            case.string,
            count=case.count,
        )
        expected = _invoke_helper(
            expected_pattern,
            case.helper,
            case.replacement,
            case.string,
            count=case.count,
        )
        return observed, expected

    observed = _invoke_helper(
        backend,
        case.helper,
        case.pattern,
        case.replacement,
        case.string,
        count=case.count,
    )
    expected = _invoke_helper(
        re,
        case.helper,
        case.pattern,
        case.replacement,
        case.string,
        count=case.count,
    )
    return observed, expected


REPLACEMENT_SURFACE_SPECS = (
    ReplacementSurfaceSpec(
        id="open-ended-quantified-group-replacement",
        bundle_specs=(
            FixtureBundleSpec(
                "nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
                expected_manifest_id=(
                    "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows"
                ),
                expected_case_ids=frozenset(
                    {
                        "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                        "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                        "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                        "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                        "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                        "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                        "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                        "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a((b|c){1,})\2d",
                        r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
                expected_manifest_id=(
                    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows"
                ),
                expected_case_ids=frozenset(
                    {
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a((b|c){2,})\2d",
                        r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py",
                expected_manifest_id=(
                    NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID
                ),
                expected_case_ids=frozenset(
                    {
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-bytes",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-bytes",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-bytes",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-bytes",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a((b|c){2,})\2(?(2)d|e)",
                        r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                        rb"a((b|c){2,})\2(?(2)d|e)",
                        rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                    }
                ),
                expected_operation_helper_counts=MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS,
                expected_text_models=MIXED_TEXT_MODELS,
            ),
        ),
        pattern_extractor=case_pattern,
        compile_patterns=(
            r"a((b|c){1,})\2d",
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        ),
        template_expand_manifest_ids=(
            "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows",
        ),
        supplemental_no_match_cases=OPEN_ENDED_SUPPLEMENTAL_NO_MATCH_CASES,
        supplemental_repeated_cases=OPEN_ENDED_SUPPLEMENTAL_REPEATED_CASES,
        pending_bytes_follow_on_manifest_ids=frozenset(
            {NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID}
        ),
    ),
    ReplacementSurfaceSpec(
        id="conditional-group-exists-replacement",
        bundle_specs=(
            FixtureBundleSpec(
                "conditional_group_exists_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-replacement-present-str",
                        "module-subn-conditional-group-exists-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-replacement-present-str",
                        "pattern-subn-conditional-group-exists-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-replacement-present-str",
                        "module-subn-named-conditional-group-exists-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)d|e)",
                        r"a(?P<word>b)?c(?(word)d|e)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_replacement_template_workflows.py",
                expected_manifest_id="conditional-group-exists-replacement-template-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-template-conditional-group-exists-replacement-present-str",
                        "module-subn-template-conditional-group-exists-replacement-absent-str",
                        "pattern-sub-template-conditional-group-exists-replacement-present-str",
                        "pattern-subn-template-conditional-group-exists-replacement-absent-str",
                        "module-sub-template-named-conditional-group-exists-replacement-present-str",
                        "module-subn-template-named-conditional-group-exists-replacement-absent-str",
                        "pattern-sub-template-named-conditional-group-exists-replacement-present-str",
                        "pattern-subn-template-named-conditional-group-exists-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)d|e)",
                        r"a(?P<word>b)?c(?(word)d|e)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_no_else_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-no-else-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-no-else-replacement-present-str",
                        "module-subn-conditional-group-exists-no-else-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-no-else-replacement-present-str",
                        "pattern-subn-conditional-group-exists-no-else-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-no-else-replacement-present-str",
                        "module-subn-named-conditional-group-exists-no-else-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-no-else-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-no-else-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)d)",
                        r"a(?P<word>b)?c(?(word)d)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_empty_else_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-empty-else-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-empty-else-replacement-present-str",
                        "module-subn-conditional-group-exists-empty-else-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-empty-else-replacement-present-str",
                        "pattern-subn-conditional-group-exists-empty-else-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-empty-else-replacement-present-str",
                        "module-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-empty-else-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)d|)",
                        r"a(?P<word>b)?c(?(word)d|)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_empty_yes_else_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-empty-yes-else-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
                        "module-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
                        "pattern-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
                        "module-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)|e)",
                        r"a(?P<word>b)?c(?(word)|e)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_fully_empty_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-fully-empty-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-fully-empty-replacement-present-str",
                        "module-subn-conditional-group-exists-fully-empty-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-fully-empty-replacement-present-str",
                        "pattern-subn-conditional-group-exists-fully-empty-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
                        "module-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)|)",
                        r"a(?P<word>b)?c(?(word)|)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_alternation_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-alternation-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-alternation-replacement-present-first-arm-str",
                        "module-subn-conditional-group-exists-alternation-replacement-present-second-arm-str",
                        "pattern-sub-conditional-group-exists-alternation-replacement-absent-first-arm-str",
                        "pattern-subn-conditional-group-exists-alternation-replacement-absent-second-arm-str",
                        "module-sub-named-conditional-group-exists-alternation-replacement-present-first-arm-str",
                        "module-subn-named-conditional-group-exists-alternation-replacement-present-second-arm-str",
                        "pattern-sub-named-conditional-group-exists-alternation-replacement-absent-first-arm-str",
                        "pattern-subn-named-conditional-group-exists-alternation-replacement-absent-second-arm-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)(de|df)|(eg|eh))",
                        r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_nested_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-nested-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-nested-replacement-present-str",
                        "module-subn-conditional-group-exists-nested-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-nested-replacement-present-str",
                        "pattern-subn-conditional-group-exists-nested-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-nested-replacement-present-str",
                        "module-subn-named-conditional-group-exists-nested-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-nested-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-nested-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)(?(1)d|e)|f)",
                        r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_quantified_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-quantified-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-quantified-replacement-present-str",
                        "module-subn-conditional-group-exists-quantified-replacement-absent-str",
                        "pattern-sub-conditional-group-exists-quantified-replacement-present-str",
                        "pattern-subn-conditional-group-exists-quantified-replacement-absent-str",
                        "module-sub-named-conditional-group-exists-quantified-replacement-present-str",
                        "module-subn-named-conditional-group-exists-quantified-replacement-absent-str",
                        "pattern-sub-named-conditional-group-exists-quantified-replacement-present-str",
                        "pattern-subn-named-conditional-group-exists-quantified-replacement-absent-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)d|e){2}",
                        r"a(?P<word>b)?c(?(word)d|e){2}",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "conditional_group_exists_quantified_alternation_replacement_workflows.py",
                expected_manifest_id="conditional-group-exists-quantified-alternation-replacement-workflows",
                expected_case_ids=frozenset(
                    {
                        "module-sub-conditional-group-exists-quantified-alternation-replacement-present-first-arm-str",
                        "module-subn-conditional-group-exists-quantified-alternation-replacement-present-second-arm-str",
                        "pattern-sub-conditional-group-exists-quantified-alternation-replacement-absent-first-arm-str",
                        "pattern-subn-conditional-group-exists-quantified-alternation-replacement-absent-second-arm-str",
                        "module-sub-named-conditional-group-exists-quantified-alternation-replacement-present-first-arm-str",
                        "module-subn-named-conditional-group-exists-quantified-alternation-replacement-present-second-arm-str",
                        "pattern-sub-named-conditional-group-exists-quantified-alternation-replacement-absent-first-arm-str",
                        "pattern-subn-named-conditional-group-exists-quantified-alternation-replacement-absent-second-arm-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
                        r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
        ),
        pattern_extractor=str_case_pattern,
        match_snapshot_manifest_ids=(
            "conditional-group-exists-replacement-workflows",
            "conditional-group-exists-replacement-template-workflows",
            "conditional-group-exists-no-else-replacement-workflows",
            "conditional-group-exists-empty-else-replacement-workflows",
            "conditional-group-exists-empty-yes-else-replacement-workflows",
            "conditional-group-exists-fully-empty-replacement-workflows",
            "conditional-group-exists-alternation-replacement-workflows",
            "conditional-group-exists-nested-replacement-workflows",
            "conditional-group-exists-quantified-replacement-workflows",
            "conditional-group-exists-quantified-alternation-replacement-workflows",
        ),
        template_expand_manifest_ids=(
            "conditional-group-exists-replacement-template-workflows",
        ),
        selector_fixture_paths=CONDITIONAL_REPLACEMENT_SELECTOR_FIXTURE_PATHS,
        known_uncovered_published_fixture_filenames=(
            KNOWN_UNCOVERED_PUBLISHED_FIXTURE_FILENAMES
        ),
        discover_no_match_on_all_replacement_cases=True,
        no_match_text_candidates=NO_MATCH_TEXT_CANDIDATES,
        supplemental_repeated_cases=CONDITIONAL_SUPPLEMENTAL_REPEATED_CASES,
    ),
)
REPLACEMENT_SURFACES = tuple(
    _load_surface(spec) for spec in REPLACEMENT_SURFACE_SPECS
)
OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE = next(
    surface
    for surface in REPLACEMENT_SURFACES
    if surface.spec.id == "open-ended-quantified-group-replacement"
)
PENDING_BYTES_REPLACEMENT_BUNDLE = next(
    bundle
    for bundle in OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE.bundles
    if bundle.expected_manifest_id
    == NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID
)

SELECTOR_SURFACE_PARAMS = tuple(
    pytest.param(surface, id=surface.spec.id)
    for surface in REPLACEMENT_SURFACES
    if surface.spec.selector_fixture_paths
)
BUNDLE_PARAMS = tuple(
    pytest.param(surface, bundle, id=bundle.expected_manifest_id)
    for surface in REPLACEMENT_SURFACES
    for bundle in surface.bundles
)
COMPILE_PATTERN_PARAMS = tuple(
    pytest.param(surface, pattern, id=_pattern_param_id(pattern))
    for surface in REPLACEMENT_SURFACES
    for pattern in surface.spec.compile_patterns
)
MODULE_CASE_PARAMS = tuple(
    pytest.param(case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.module_cases
)
PATTERN_CASE_PARAMS = tuple(
    pytest.param(case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.pattern_cases
)
MATCH_SNAPSHOT_CASE_PARAMS = tuple(
    pytest.param(surface, case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.match_snapshot_cases
)
TEMPLATE_EXPAND_CASE_PARAMS = tuple(
    pytest.param(surface, case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.template_expand_cases
)
DISCOVERED_NO_MATCH_CASE_PARAMS = tuple(
    pytest.param(surface, case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.discovered_no_match_cases
)
SUPPLEMENTAL_NO_MATCH_CASE_PARAMS = tuple(
    pytest.param(case, id=case.id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.spec.supplemental_no_match_cases
)
SUPPLEMENTAL_REPEATED_CASE_PARAMS = tuple(
    pytest.param(case, id=case.id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.spec.supplemental_repeated_cases
)


@pytest.mark.parametrize("surface", SELECTOR_SURFACE_PARAMS)
def test_replacement_parity_suite_tracks_published_fixture_coverage_frontier(
    surface: LoadedReplacementSurface,
) -> None:
    assert surface.spec.selector_fixture_paths

    covered_paths = published_fixture_paths_from_bundles(surface.bundles)
    uncovered_paths = tuple(
        path
        for path in surface.spec.selector_fixture_paths
        if path not in covered_paths
    )
    assert covered_paths
    assert tuple(path.name for path in uncovered_paths) == (
        surface.spec.known_uncovered_published_fixture_filenames
    )
    assert tuple(
        sorted((*covered_paths, *uncovered_paths), key=lambda path: path.name)
    ) == surface.spec.selector_fixture_paths


@pytest.mark.parametrize(("surface", "bundle"), BUNDLE_PARAMS)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    surface: LoadedReplacementSurface,
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=surface.spec.pattern_extractor,
    )


def test_mixed_replacement_manifest_keeps_bytes_rows_explicit_as_pending_follow_on(
) -> None:
    bundle = PENDING_BYTES_REPLACEMENT_BUNDLE
    surface = OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE
    str_case_ids = frozenset(
        case.case_id for case in bundle.cases if case.text_model == "str"
    )
    bytes_case_ids = frozenset(
        case.case_id for case in bundle.cases if case.text_model == "bytes"
    )
    expected_module_case_ids = frozenset(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "module_call")
        if case.text_model == "str"
    )
    expected_pattern_case_ids = frozenset(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
        if case.text_model == "str"
    )
    shared_module_case_ids = frozenset(
        case.case_id
        for case in surface.module_cases
        if case.manifest_id == bundle.expected_manifest_id
    )
    shared_pattern_case_ids = frozenset(
        case.case_id
        for case in surface.pattern_cases
        if case.manifest_id == bundle.expected_manifest_id
    )
    shared_template_expand_case_ids = frozenset(
        case.case_id
        for case in surface.template_expand_cases
        if case.manifest_id == bundle.expected_manifest_id
    )

    assert {case.text_model for case in bundle.cases} == MIXED_TEXT_MODELS
    assert len(str_case_ids) == len(bytes_case_ids) == 8
    assert bytes_case_ids == {
        f"{case_id.removesuffix('-str')}-bytes" for case_id in str_case_ids
    }
    assert shared_module_case_ids == expected_module_case_ids
    assert shared_pattern_case_ids == expected_pattern_case_ids
    assert shared_template_expand_case_ids == str_case_ids


@pytest.mark.parametrize(("surface", "pattern"), COMPILE_PATTERN_PARAMS)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    surface: LoadedReplacementSurface,
    pattern: TextValue,
) -> None:
    del surface
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, pattern)


@pytest.mark.parametrize("case", MODULE_CASE_PARAMS)
def test_module_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASE_PARAMS)
def test_pattern_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize(("surface", "case"), MATCH_SNAPSHOT_CASE_PARAMS)
def test_replacement_match_snapshot_matches_cpython(
    regex_backend: tuple[str, object],
    surface: LoadedReplacementSurface,
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed_match, expected_match = _search_match_for_case(
        surface,
        backend_name,
        backend,
        case,
    )

    assert_match_parity(
        backend_name,
        observed_match,
        expected_match,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed_match, expected_match)


@pytest.mark.parametrize(("surface", "case"), TEMPLATE_EXPAND_CASE_PARAMS)
def test_replacement_template_match_expand_matches_cpython(
    regex_backend: tuple[str, object],
    surface: LoadedReplacementSurface,
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    template = case_replacement_argument(case)
    assert isinstance(template, (str, bytes))
    observed_match, expected_match = _search_match_for_case(
        surface,
        backend_name,
        backend,
        case,
    )

    assert_match_parity(
        backend_name,
        observed_match,
        expected_match,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed_match, expected_match)

    observed = observed_match.expand(template)
    expected = expected_match.expand(template)

    assert type(observed) is type(expected)
    assert observed == expected


@pytest.mark.parametrize(("surface", "case"), DISCOVERED_NO_MATCH_CASE_PARAMS)
def test_discovered_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    surface: LoadedReplacementSurface,
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    text = _no_match_text(surface, case)
    observed = _run_replacement_case(backend, case, text=text)
    expected = _run_replacement_case(re, case, text=text)
    expected_result: ReplacementOutcome
    if case.helper == "sub":
        expected_result = text
    else:
        expected_result = (text, 0)

    assert observed == expected == expected_result


@pytest.mark.parametrize("case", SUPPLEMENTAL_NO_MATCH_CASE_PARAMS)
def test_supplemental_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalReplacementCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _run_supplemental_replacement_case(
        backend_name,
        backend,
        case,
    )

    expected_result: ReplacementOutcome
    if case.helper == "sub":
        expected_result = case.string
    else:
        expected_result = (case.string, 0)

    assert observed == expected == expected_result


@pytest.mark.parametrize("case", SUPPLEMENTAL_REPEATED_CASE_PARAMS)
def test_repeated_replacement_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalReplacementCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _run_supplemental_replacement_case(
        backend_name,
        backend,
        case,
    )

    assert case.expected_result is not None
    assert observed == expected == case.expected_result


def test_sorted_compile_patterns_supports_mixed_text_models() -> None:
    (bundle,) = load_fixture_bundles(
        (
            FixtureBundleSpec(
                fixture_name="open_ended_quantified_group_alternation_workflows.py",
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

    assert _sorted_compile_patterns(
        bundle.cases,
        pattern_extractor=case_pattern,
    ) == (
        r"a(?P<word>bc|de){1,}d",
        r"a(bc|de){1,}d",
        rb"a(?P<word>bc|de){1,}d",
        rb"a(bc|de){1,}d",
    )


def test_no_match_text_filters_candidates_by_case_text_model() -> None:
    str_case = FixtureCase(
        case_id="synthetic-str-replacement",
        manifest_id="synthetic-replacement",
        suite_id="synthetic.replacement",
        layer="module_workflow",
        family="synthetic_replacement_case",
        operation="module_call",
        notes=[],
        categories=[],
        pattern=None,
        flags=0,
        text_model="str",
        pattern_encoding="latin-1",
        helper="sub",
        source_args=[r"a(bc|de){1,}d", "x", "abcd"],
        source_kwargs={},
        args=[r"a(bc|de){1,}d", "x", "abcd"],
        kwargs={},
    )
    bytes_case = FixtureCase(
        case_id="synthetic-bytes-replacement",
        manifest_id="synthetic-replacement",
        suite_id="synthetic.replacement",
        layer="module_workflow",
        family="synthetic_replacement_case",
        operation="module_call",
        notes=[],
        categories=[],
        pattern=None,
        flags=0,
        text_model="bytes",
        pattern_encoding="latin-1",
        helper="sub",
        source_args=[rb"a(bc|de){1,}d", b"x", b"abcd"],
        source_kwargs={},
        args=[rb"a(bc|de){1,}d", b"x", b"abcd"],
        kwargs={},
    )
    surface = LoadedReplacementSurface(
        spec=ReplacementSurfaceSpec(
            id="mixed-no-match-candidate-contract",
            bundle_specs=(),
            pattern_extractor=case_pattern,
            no_match_text_candidates=("zzzz", b"zzzz"),
        ),
        bundles=(),
        replacement_cases=(),
        module_cases=(),
        pattern_cases=(),
        match_snapshot_cases=(),
        template_expand_cases=(),
        discovered_no_match_cases=(),
    )

    assert _no_match_text(surface, str_case) == "zzzz"
    assert _no_match_text(surface, bytes_case) == b"zzzz"
