from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
import pathlib
import re

import pytest

import rebar

from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    CpythonReAdapter,
    FixtureCase,
    RebarAdapter,
    evaluate_case,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
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
NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID = (
    "nested-broader-range-open-ended-quantified-group-alternation-"
    "branch-local-backreference-replacement-workflows"
)
NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID = (
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
    "branch-local-backreference-replacement-workflows"
)
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
GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID = "grouped-replacement-template"
GROUPED_TEMPLATE_SELECTED_CASE_ID = "module-sub-grouping-template"
GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS = (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
)
GROUPED_REPLACEMENT_NAMED_CASE_IDS = (
    "module-sub-template-named-group-str",
    "module-subn-template-named-group-str",
    "pattern-sub-template-named-group-str",
    "pattern-subn-template-named-group-str",
)
NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS = (
    "module-sub-template-nested-group-alternation-numbered-outer-str",
    "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    "module-sub-template-nested-group-alternation-numbered-wrapper-str",
    "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
)
GROUPED_TEMPLATE_OPERATION_HELPER_COUNTS = Counter({("module_call", "sub"): 1})
NESTED_GROUP_ALTERNATION_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
GROUPED_REPLACEMENT_SHARED_GROUP_KIND_COUNTS = Counter(
    {
        ("module_call", "sub", "numbered"): 1,
        ("module_call", "sub", "named"): 1,
        ("module_call", "subn", "numbered"): 1,
        ("module_call", "subn", "named"): 1,
        ("pattern_call", "sub", "numbered"): 1,
        ("pattern_call", "sub", "named"): 1,
        ("pattern_call", "subn", "numbered"): 1,
        ("pattern_call", "subn", "named"): 1,
    }
)
GROUPED_REPLACEMENT_NESTED_ALTERNATION_GROUP_KIND_COUNTS = Counter(
    {
        ("module_call", "sub", "numbered"): 2,
        ("pattern_call", "subn", "named"): 2,
    }
)
GROUPED_REPLACEMENT_BUNDLE_CONTRACT_MANIFEST_IDS = frozenset(
    {
        "grouped-alternation-replacement-workflows",
        "nested-group-replacement-workflows",
        "nested-group-alternation-replacement-workflows",
        "quantified-nested-group-replacement-workflows",
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
    }
)
GROUPED_REPLACEMENT_MATCH_GROUP_ACCESS_MANIFEST_IDS = (
    "named-group-replacement-workflows",
)
GROUPED_REPLACEMENT_TEMPLATE_EXPAND_MANIFEST_IDS = (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
)
GROUPED_REPLACEMENT_COMPILE_PATTERNS = (
    "(?P<word>abc)",
    "(abc)",
    "a((b))d",
    "a((bc)+)d",
    "a((b|c))d",
    r"a((b|c){1,4})\2d",
    "a(?P<outer>(?P<inner>b))d",
    "a(?P<outer>(?P<inner>bc)+)d",
    r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
    "a(?P<outer>(b|c))d",
    "a(?P<word>b|c)d",
    "a(b|c)d",
)
DIRECT_LITERAL_MODULE_REPLACEMENT_CASES = [
    pytest.param("abc", "x", "zzz", 0, id="str-no-match"),
    pytest.param("abc", "x", "zabczz", 0, id="str-single-match"),
    pytest.param("abc", "x", "abcabc", 0, id="str-repeated-match"),
    pytest.param("abc", "x", "abcabc", 1, id="str-count-one"),
    pytest.param("abc", "x", "abcabc", -1, id="str-negative-count"),
    pytest.param(b"abc", b"x", b"zzz", 0, id="bytes-no-match"),
    pytest.param(b"abc", b"x", b"zabcabc", 0, id="bytes-repeated-match"),
    pytest.param(b"abc", b"x", b"abcabc", 1, id="bytes-count-one"),
]
DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES = [
    pytest.param("abc", "x", "zzz", 0, id="str-no-match"),
    pytest.param("abc", "x", "zabczz", 0, id="str-single-match"),
    pytest.param("abc", "x", "abcabc", 0, id="str-repeated-match"),
    pytest.param("abc", "x", "abcabc", 1, id="str-count-one"),
    pytest.param("abc", "x", "abcabc", -1, id="str-negative-count"),
    pytest.param(b"abc", b"x", b"abcabc", 0, id="bytes-repeated-match"),
    pytest.param(b"abc", b"x", b"zabczz", 0, id="bytes-single-match"),
]
DIRECT_WHOLE_MATCH_TEMPLATE_REPLACEMENT_CASES = [
    pytest.param("abc", r"\g<0>x", "abc", 0, id="single-match"),
    pytest.param("abc", r"\g<0>x", "abcabc", 0, id="repeated-matches"),
    pytest.param("abc", r"\g<0>x", "abcabc", 1, id="count-one"),
]


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
class ReplacementParityCase:
    fixture_case: FixtureCase
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None

    def __getattr__(self, attribute: str) -> object:
        return getattr(self.fixture_case, attribute)


@dataclass(frozen=True)
class ReplacementSurfaceSpec:
    id: str
    bundle_specs: tuple[FixtureBundleSpec, ...]
    pattern_extractor: Callable[[FixtureCase], TextValue]
    compile_patterns: tuple[TextValue, ...] = ()
    match_snapshot_manifest_ids: tuple[str, ...] = ()
    match_group_access_manifest_ids: tuple[str, ...] = ()
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
    match_group_access_cases: tuple[FixtureCase, ...]
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

GROUPED_REPLACEMENT_SUPPLEMENTAL_NO_MATCH_CASES = (
    SupplementalReplacementCase(
        id="module-sub-template-named-group-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"(?P<word>abc)",
        replacement=r"<\g<word>>",
        string="xyzxyz",
    ),
    SupplementalReplacementCase(
        id="module-subn-template-named-group-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"(?P<word>abc)",
        replacement=r"<\g<word>>",
        string="xyzxyz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-sub-template-named-group-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"(?P<word>abc)",
        replacement=r"<\g<word>>",
        string="xyzxyz",
    ),
    SupplementalReplacementCase(
        id="pattern-subn-template-named-group-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"(?P<word>abc)",
        replacement=r"<\g<word>>",
        string="xyzxyz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="module-numbered-nested-group-sub-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a((b))d",
        replacement=r"\1x",
        string="zzadzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="module-numbered-nested-group-subn-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a((b))d",
        replacement=r"\2x",
        string="zzadzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-numbered-nested-group-sub-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a((b))d",
        replacement=r"\1x",
        string="zzadzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="pattern-numbered-nested-group-subn-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a((b))d",
        replacement=r"\2x",
        string="zzadzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="module-named-nested-group-sub-no-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b))d",
        replacement=r"\g<outer>x",
        string="zzadzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="module-named-nested-group-subn-no-match",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b))d",
        replacement=r"\g<inner>x",
        string="zzadzz",
        count=1,
    ),
    SupplementalReplacementCase(
        id="pattern-named-nested-group-sub-no-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"a(?P<outer>(?P<inner>b))d",
        replacement=r"\g<outer>x",
        string="zzadzz",
        count=0,
    ),
    SupplementalReplacementCase(
        id="pattern-named-nested-group-subn-no-match",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a(?P<outer>(?P<inner>b))d",
        replacement=r"\g<inner>x",
        string="zzadzz",
        count=1,
    ),
)

GROUPED_REPLACEMENT_SUPPLEMENTAL_REPEATED_CASES = (
    SupplementalReplacementCase(
        id="module-grouped-template-sub-single-match",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abc",
        count=0,
        expected_result="abcx",
    ),
    SupplementalReplacementCase(
        id="module-grouped-template-sub-repeated",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abcabc",
        count=0,
        expected_result="abcxabcx",
    ),
    SupplementalReplacementCase(
        id="module-grouped-template-subn-first-match-only",
        use_compiled_pattern=False,
        helper="subn",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abcabc",
        count=1,
        expected_result=("abcxabc", 1),
    ),
    SupplementalReplacementCase(
        id="pattern-grouped-template-sub-single-match",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abc",
        count=0,
        expected_result="abcx",
    ),
    SupplementalReplacementCase(
        id="pattern-grouped-template-sub-repeated",
        use_compiled_pattern=True,
        helper="sub",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abcabc",
        count=0,
        expected_result="abcxabcx",
    ),
    SupplementalReplacementCase(
        id="pattern-grouped-template-subn-first-match-only",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abcabc",
        count=1,
        expected_result=("abcxabc", 1),
    ),
)
SUPPLEMENTAL_NEGATIVE_COUNT_CASES = (
    SupplementalReplacementCase(
        id="module-grouped-template-negative-count",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"(abc)",
        replacement=r"\1x",
        string="abcabc",
        count=-1,
        expected_result="abcabc",
    ),
    SupplementalReplacementCase(
        id="pattern-named-group-template-negative-count",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"(?P<word>abc)",
        replacement=r"<\g<word>>",
        string="abcabc",
        count=-1,
        expected_result=("abcabc", 0),
    ),
    SupplementalReplacementCase(
        id="module-conditional-template-negative-count",
        use_compiled_pattern=False,
        helper="sub",
        pattern=r"a(b)?c(?(1)d|e)",
        replacement=r"\1x",
        string="abcdaceabcd",
        count=-1,
        expected_result="abcdaceabcd",
    ),
    SupplementalReplacementCase(
        id="pattern-named-conditional-template-negative-count",
        use_compiled_pattern=True,
        helper="subn",
        pattern=r"a(?P<word>b)?c(?(word)d|e)",
        replacement=r"\g<word>x",
        string="abcdaceabcd",
        count=-1,
        expected_result=("abcdaceabcd", 0),
    ),
    SupplementalReplacementCase(
        id="module-numbered-bytes-template-negative-count",
        use_compiled_pattern=False,
        helper="sub",
        pattern=rb"a((b|c){2,})\2(?(2)d|e)",
        replacement=rb"\1x",
        string=b"abbbdzzabcccd",
        count=-1,
        expected_result=b"abbbdzzabcccd",
    ),
    SupplementalReplacementCase(
        id="pattern-named-bytes-template-negative-count",
        use_compiled_pattern=True,
        helper="subn",
        pattern=rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        replacement=rb"\g<inner>x",
        string=b"abbbdzzabcccd",
        count=-1,
        expected_result=(b"abbbdzzabcccd", 0),
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


def _compiled_str_pattern(case: FixtureCase) -> re.Pattern[str]:
    return re.compile(str_case_pattern(case), case.flags or 0)


def _grouped_replacement_group_kind(case: FixtureCase) -> str:
    return "named" if _compiled_str_pattern(case).groupindex else "numbered"


def _expected_grouped_replacement_template(case: FixtureCase) -> str:
    compiled = _compiled_str_pattern(case)
    target_group_index = (
        1
        if case.helper == "sub" or "outer-capture" in case.categories
        else compiled.groups
    )
    if compiled.groupindex:
        group_names_by_index = {
            index: group_name for group_name, index in compiled.groupindex.items()
        }
        replacement = rf"\g<{group_names_by_index[target_group_index]}>"
    else:
        replacement = rf"\{target_group_index}"
    if "wrapper-template" in case.categories:
        return f"<{replacement}>"
    if compiled.groupindex and compiled.pattern == r"(?P<word>abc)":
        return f"<{replacement}>"
    return f"{replacement}x"


def _assert_grouped_replacement_fixture_bundle_contract(bundle: FixtureBundle) -> None:
    expected_group_kind_counts = (
        GROUPED_REPLACEMENT_NESTED_ALTERNATION_GROUP_KIND_COUNTS
        if bundle.expected_manifest_id == "nested-group-alternation-replacement-workflows"
        else GROUPED_REPLACEMENT_SHARED_GROUP_KIND_COUNTS
    )
    assert Counter(
        (case.operation, case.helper, _grouped_replacement_group_kind(case))
        for case in bundle.cases
    ) == expected_group_kind_counts

    for case in bundle.cases:
        compiled = _compiled_str_pattern(case)
        count_index = 3 if case.operation == "module_call" else 2

        assert case.kwargs == {}
        assert "replacement-template" in case.categories
        assert "str" in case.categories
        assert case.helper in {"sub", "subn"}
        assert case.helper in case.categories
        if case.operation == "module_call":
            assert "module" in case.categories
        else:
            assert "pattern" in case.categories

        if compiled.groupindex:
            assert "named-group" in case.categories

        assert case_replacement_argument(case) == _expected_grouped_replacement_template(case)
        if case.helper == "sub":
            assert len(case.args) == count_index
        else:
            assert len(case.args) == count_index + 1
            assert case.args[count_index] == 1


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
        match_group_access_cases=_cases_for_manifest_ids(
            replacement_cases,
            spec.match_group_access_manifest_ids,
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


def _replacement_parity_case(case: FixtureCase) -> ReplacementParityCase:
    return ReplacementParityCase(fixture_case=case)


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
        id=GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID,
        bundle_specs=(
            FixtureBundleSpec(
                "collection_replacement_workflows.py",
                expected_manifest_id="collection-replacement-workflows",
                selected_case_ids=(GROUPED_TEMPLATE_SELECTED_CASE_ID,),
                expected_patterns=frozenset({"(abc)"}),
                expected_operation_helper_counts=GROUPED_TEMPLATE_OPERATION_HELPER_COUNTS,
                expected_text_models=frozenset({"str"}),
            ),
            FixtureBundleSpec(
                "named_group_replacement_workflows.py",
                expected_manifest_id="named-group-replacement-workflows",
                expected_patterns=frozenset({r"(?P<word>abc)"}),
                expected_operation_helper_counts=Counter(
                    {
                        ("module_call", "sub"): 1,
                        ("module_call", "subn"): 1,
                        ("pattern_call", "sub"): 1,
                        ("pattern_call", "subn"): 1,
                    }
                ),
            ),
            FixtureBundleSpec(
                "grouped_alternation_replacement_workflows.py",
                expected_manifest_id="grouped-alternation-replacement-workflows",
                expected_patterns=frozenset(
                    {
                        r"a(b|c)d",
                        r"a(?P<word>b|c)d",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "nested_group_replacement_workflows.py",
                expected_manifest_id="nested-group-replacement-workflows",
                expected_patterns=frozenset(
                    {
                        r"a((b))d",
                        r"a(?P<outer>(?P<inner>b))d",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                "nested_group_alternation_replacement_workflows.py",
                expected_manifest_id="nested-group-alternation-replacement-workflows",
                expected_patterns=frozenset(
                    {
                        r"a((b|c))d",
                        r"a(?P<outer>(b|c))d",
                    }
                ),
                expected_operation_helper_counts=(
                    NESTED_GROUP_ALTERNATION_OPERATION_HELPER_COUNTS
                ),
            ),
            FixtureBundleSpec(
                "quantified_nested_group_replacement_workflows.py",
                expected_manifest_id="quantified-nested-group-replacement-workflows",
                expected_patterns=frozenset(
                    {
                        r"a((bc)+)d",
                        r"a(?P<outer>(?P<inner>bc)+)d",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
            FixtureBundleSpec(
                (
                    "nested_broader_range_wider_ranged_repeat_quantified_group_"
                    "alternation_branch_local_backreference_replacement_"
                    "workflows.py"
                ),
                expected_manifest_id=(
                    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID
                ),
                expected_case_ids=frozenset(
                    {
                        "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                        "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                        "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                        "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                        "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                        "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                        "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
                        "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a((b|c){1,4})\2d",
                        r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                    }
                ),
                expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            ),
        ),
        pattern_extractor=str_case_pattern,
        compile_patterns=GROUPED_REPLACEMENT_COMPILE_PATTERNS,
        match_group_access_manifest_ids=GROUPED_REPLACEMENT_MATCH_GROUP_ACCESS_MANIFEST_IDS,
        template_expand_manifest_ids=GROUPED_REPLACEMENT_TEMPLATE_EXPAND_MANIFEST_IDS,
        supplemental_no_match_cases=GROUPED_REPLACEMENT_SUPPLEMENTAL_NO_MATCH_CASES,
        supplemental_repeated_cases=GROUPED_REPLACEMENT_SUPPLEMENTAL_REPEATED_CASES,
    ),
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
                    NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID
                ),
                expected_case_ids=frozenset(
                    {
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-bytes",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
                    }
                ),
                expected_patterns=frozenset(
                    {
                        r"a((b|c){2,})\2d",
                        r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
                        rb"a((b|c){2,})\2d",
                        rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
                    }
                ),
                expected_operation_helper_counts=MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS,
                expected_text_models=MIXED_TEXT_MODELS,
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
            rb"a((b|c){2,})\2(?(2)d|e)",
            rb"a((b|c){2,})\2d",
            rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        ),
        match_group_access_manifest_ids=(
            NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID,
        ),
        template_expand_manifest_ids=(
            "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
            NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows",
        ),
        supplemental_no_match_cases=OPEN_ENDED_SUPPLEMENTAL_NO_MATCH_CASES,
        supplemental_repeated_cases=OPEN_ENDED_SUPPLEMENTAL_REPEATED_CASES,
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
GROUPED_REPLACEMENT_TEMPLATE_SURFACE = next(
    surface
    for surface in REPLACEMENT_SURFACES
    if surface.spec.id == GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID
)
OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE = next(
    surface
    for surface in REPLACEMENT_SURFACES
    if surface.spec.id == "open-ended-quantified-group-replacement"
)
MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE = next(
    bundle
    for bundle in OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE.bundles
    if bundle.expected_manifest_id
    == NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID
)
BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE = next(
    bundle
    for bundle in OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE.bundles
    if bundle.expected_manifest_id == NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID
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
    pytest.param(_replacement_parity_case(case), id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.module_cases
)
PATTERN_CASE_PARAMS = tuple(
    pytest.param(_replacement_parity_case(case), id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.pattern_cases
)
MATCH_SNAPSHOT_CASE_PARAMS = tuple(
    pytest.param(surface, case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.match_snapshot_cases
)
MATCH_GROUP_ACCESS_CASE_PARAMS = tuple(
    pytest.param(surface, case, id=case.case_id)
    for surface in REPLACEMENT_SURFACES
    for case in surface.match_group_access_cases
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
SUPPLEMENTAL_NEGATIVE_COUNT_CASE_PARAMS = tuple(
    pytest.param(case, id=case.id) for case in SUPPLEMENTAL_NEGATIVE_COUNT_CASES
)
PENDING_REBAR_REPLACEMENT_CASE_IDS = frozenset(
    case.case_id
    for surface in REPLACEMENT_SURFACES
    for case in surface.replacement_cases
    if "rebar" in _replacement_parity_case(case).unsupported_backends
)
PENDING_REBAR_REPLACEMENT_MANIFEST_IDS = frozenset(
    case.manifest_id
    for surface in REPLACEMENT_SURFACES
    for case in surface.replacement_cases
    if "rebar" in _replacement_parity_case(case).unsupported_backends
)


def _live_unimplemented_replacement_cases() -> tuple[FixtureCase, ...]:
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    return tuple(
        case
        for surface in REPLACEMENT_SURFACES
        for case in surface.replacement_cases
        if evaluate_case(case, cpython_adapter, rebar_adapter)["comparison"]
        == "unimplemented"
    )


def _is_pending_bytes_follow_on_case(
    surface: LoadedReplacementSurface,
    case: FixtureCase,
) -> bool:
    return (
        case.text_model == "bytes"
        and case.manifest_id in surface.spec.pending_bytes_follow_on_manifest_ids
    )


def _expected_selected_replacement_case_ids(
    surface: LoadedReplacementSurface,
    *,
    manifest_id: str | None = None,
) -> tuple[str, ...]:
    return tuple(
        case.case_id
        for bundle in surface.bundles
        if manifest_id is None or bundle.expected_manifest_id == manifest_id
        for case in bundle.cases
        if not _is_pending_bytes_follow_on_case(surface, case)
    )


def _expected_uncovered_replacement_case_ids(
    surface: LoadedReplacementSurface,
    manifest_id: str,
) -> tuple[str, ...]:
    return tuple(
        case.case_id
        for bundle in surface.bundles
        if bundle.expected_manifest_id == manifest_id
        for case in bundle.cases
        if _is_pending_bytes_follow_on_case(surface, case)
    )


def _replacement_direct_test_case_id_buckets(
    surface: LoadedReplacementSurface,
) -> dict[str, frozenset[str]]:
    return {
        "module": frozenset(case.case_id for case in surface.module_cases),
        "pattern": frozenset(case.case_id for case in surface.pattern_cases),
    }


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
    if (
        surface.spec.id == GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID
        and bundle.expected_manifest_id in GROUPED_REPLACEMENT_BUNDLE_CONTRACT_MANIFEST_IDS
    ):
        _assert_grouped_replacement_fixture_bundle_contract(bundle)


def test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit() -> None:
    surface = GROUPED_REPLACEMENT_TEMPLATE_SURFACE

    assert tuple(bundle.expected_manifest_id for bundle in surface.bundles) == (
        GROUPED_REPLACEMENT_BUNDLE_MANIFEST_IDS
    )

    grouped_template_bundle = surface.bundles[0]
    assert tuple(case.case_id for case in grouped_template_bundle.cases) == (
        GROUPED_TEMPLATE_SELECTED_CASE_ID,
    )
    (grouped_template_case,) = grouped_template_bundle.cases
    assert grouped_template_case.operation == "module_call"
    assert grouped_template_case.helper == "sub"
    assert str_case_pattern(grouped_template_case) == "(abc)"
    assert case_replacement_argument(grouped_template_case) == r"\1x"
    assert case_text_argument(grouped_template_case) == "abc"
    assert "replacement-template" in grouped_template_case.categories
    assert "grouping-dependent" in grouped_template_case.categories

    named_bundle = next(
        bundle
        for bundle in surface.bundles
        if bundle.expected_manifest_id == "named-group-replacement-workflows"
    )
    assert tuple(case.case_id for case in named_bundle.cases) == (
        GROUPED_REPLACEMENT_NAMED_CASE_IDS
    )
    for case in named_bundle.cases:
        assert case_replacement_argument(case) == r"<\g<word>>"
        assert "named-group" in case.categories
        assert "replacement-template" in case.categories
        assert case.text_model == "str"

    nested_group_alternation_bundle = next(
        bundle
        for bundle in surface.bundles
        if bundle.expected_manifest_id == "nested-group-alternation-replacement-workflows"
    )
    assert tuple(case.case_id for case in nested_group_alternation_bundle.cases) == (
        NESTED_GROUP_ALTERNATION_REPLACEMENT_CASE_IDS
    )
    assert {
        case.case_id
        for case in nested_group_alternation_bundle.cases
        if "wrapper-template" in case.categories
    } == {
        "module-sub-template-nested-group-alternation-numbered-wrapper-str",
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    }


@pytest.mark.parametrize(("surface", "bundle"), BUNDLE_PARAMS)
def test_replacement_suite_tracks_published_case_frontier(
    surface: LoadedReplacementSurface,
    bundle: FixtureBundle,
) -> None:
    if len(bundle.cases) != len(bundle.manifest.cases):
        assert tuple(case.case_id for case in bundle.cases) == (
            _expected_selected_replacement_case_ids(
                surface,
                manifest_id=bundle.expected_manifest_id,
            )
        )
        return

    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=_expected_selected_replacement_case_ids(
            surface,
            manifest_id=bundle.expected_manifest_id,
        ),
        expected_uncovered_case_ids=_expected_uncovered_replacement_case_ids(
            surface,
            bundle.expected_manifest_id,
        ),
    )


@pytest.mark.parametrize("surface", SELECTOR_SURFACE_PARAMS)
def test_replacement_direct_test_buckets_cover_selected_frontier(
    surface: LoadedReplacementSurface,
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        _replacement_direct_test_case_id_buckets(surface),
        selected_case_ids=_expected_selected_replacement_case_ids(surface),
        coverage_label=f"{surface.spec.id} replacement direct-test case-id buckets",
    )


def test_pending_rebar_replacement_frontier_matches_live_unimplemented_cases() -> None:
    live_unimplemented_cases = _live_unimplemented_replacement_cases()

    assert {case.case_id for case in live_unimplemented_cases} == (
        PENDING_REBAR_REPLACEMENT_CASE_IDS
    ) == frozenset()
    assert {case.manifest_id for case in live_unimplemented_cases} == (
        PENDING_REBAR_REPLACEMENT_MANIFEST_IDS
    ) == frozenset()


def test_mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface(
) -> None:
    bundle = MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE
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
    )
    expected_pattern_case_ids = frozenset(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
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
    shared_match_group_access_case_ids = frozenset(
        case.case_id
        for case in surface.match_group_access_cases
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
    assert shared_match_group_access_case_ids == str_case_ids | bytes_case_ids
    assert shared_template_expand_case_ids == str_case_ids | bytes_case_ids


def test_broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface(
) -> None:
    bundle = BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE
    surface = OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE
    ordered_str_case_ids = tuple(
        case.case_id for case in bundle.cases if case.text_model == "str"
    )
    ordered_bytes_case_ids = tuple(
        case.case_id for case in bundle.cases if case.text_model == "bytes"
    )
    expected_module_case_ids = frozenset(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "module_call")
    )
    expected_pattern_case_ids = frozenset(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
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
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    )
    assert len(ordered_str_case_ids) == len(ordered_bytes_case_ids) == 8
    assert ordered_bytes_case_ids == tuple(
        f"{case_id.removesuffix('-str')}-bytes" for case_id in ordered_str_case_ids
    )
    assert shared_module_case_ids == expected_module_case_ids
    assert shared_pattern_case_ids == expected_pattern_case_ids
    assert shared_template_expand_case_ids == (
        frozenset(ordered_str_case_ids) | frozenset(ordered_bytes_case_ids)
    )


def test_broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier(
) -> None:
    manifest_id = NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID
    surface = _load_surface(
        ReplacementSurfaceSpec(
            id="broader-range-open-ended-replacement-mixed-contract",
            bundle_specs=(
                FixtureBundleSpec(
                    fixture_name=(
                        BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.manifest.path.name
                    ),
                    expected_manifest_id=manifest_id,
                    expected_patterns=(
                        BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.expected_patterns
                    ),
                    expected_operation_helper_counts=(
                        BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.expected_operation_helper_counts
                    ),
                    expected_case_ids=(
                        BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.expected_case_ids
                    ),
                    expected_text_models=(
                        BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.expected_text_models
                    ),
                ),
            ),
            pattern_extractor=case_pattern,
            template_expand_manifest_ids=(manifest_id,),
        )
    )
    (bundle,) = surface.bundles
    expected_case_ids = tuple(case.case_id for case in bundle.cases)
    expected_module_case_ids = tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), "module_call")
    )
    expected_pattern_case_ids = tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), "pattern_call")
    )

    assert {case.text_model for case in bundle.cases} == MIXED_TEXT_MODELS
    assert tuple(case.case_id for case in surface.replacement_cases) == expected_case_ids
    assert Counter((case.operation, case.helper) for case in surface.replacement_cases) == (
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    )
    assert tuple(case.case_id for case in surface.module_cases) == expected_module_case_ids
    assert tuple(case.case_id for case in surface.pattern_cases) == expected_pattern_case_ids
    assert tuple(case.case_id for case in surface.match_group_access_cases) == ()
    assert tuple(case.case_id for case in surface.template_expand_cases) == expected_case_ids
    assert _expected_selected_replacement_case_ids(
        surface,
        manifest_id=manifest_id,
    ) == expected_case_ids
    assert _expected_uncovered_replacement_case_ids(surface, manifest_id) == ()


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


@pytest.mark.parametrize(("surface", "case"), MATCH_GROUP_ACCESS_CASE_PARAMS)
def test_replacement_match_group_accessors_match_cpython(
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
    assert_valid_match_group_access_parity(observed_match, expected_match)


@pytest.mark.parametrize(("surface", "case"), MATCH_GROUP_ACCESS_CASE_PARAMS)
def test_replacement_invalid_group_access_errors_match_cpython(
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
    assert_invalid_match_group_access_parity(observed_match, expected_match)


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


@pytest.mark.parametrize("case", SUPPLEMENTAL_NEGATIVE_COUNT_CASE_PARAMS)
def test_negative_replacement_counts_short_circuit_like_cpython(
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
        match_group_access_cases=(),
        template_expand_cases=(),
        discovered_no_match_cases=(),
    )

    assert _no_match_text(surface, str_case) == "zzzz"
    assert _no_match_text(surface, bytes_case) == b"zzzz"


def _assert_placeholder_message(error: BaseException, expected_prefix: str) -> None:
    assert expected_prefix in str(error)


def _assert_module_replacement_parity(
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: int,
) -> None:
    assert rebar.sub(pattern, replacement, string, count=count) == re.sub(
        pattern,
        replacement,
        string,
        count=count,
    )
    assert rebar.subn(pattern, replacement, string, count=count) == re.subn(
        pattern,
        replacement,
        string,
        count=count,
    )


def _assert_pattern_replacement_parity(
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: int,
) -> None:
    observed_pattern = rebar.compile(pattern)
    expected_pattern = re.compile(pattern)

    assert observed_pattern.sub(replacement, string, count=count) == expected_pattern.sub(
        replacement,
        string,
        count=count,
    )
    assert observed_pattern.subn(
        replacement,
        string,
        count=count,
    ) == expected_pattern.subn(
        replacement,
        string,
        count=count,
    )


@pytest.mark.parametrize(
    ("pattern", "replacement", "string", "count"),
    DIRECT_LITERAL_MODULE_REPLACEMENT_CASES,
)
def test_source_package_module_literal_replacement_helpers_match_cpython(
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: int,
) -> None:
    _assert_module_replacement_parity(pattern, replacement, string, count)


@pytest.mark.parametrize(
    ("pattern", "replacement", "string", "count"),
    DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES,
)
def test_source_package_pattern_literal_replacement_helpers_match_cpython(
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: int,
) -> None:
    _assert_pattern_replacement_parity(pattern, replacement, string, count)


@pytest.mark.parametrize(
    ("pattern", "replacement", "string", "count"),
    DIRECT_WHOLE_MATCH_TEMPLATE_REPLACEMENT_CASES,
)
def test_source_package_module_whole_match_template_replacement_matches_cpython(
    pattern: str,
    replacement: str,
    string: str,
    count: int,
) -> None:
    _assert_module_replacement_parity(pattern, replacement, string, count)


@pytest.mark.parametrize(
    ("pattern", "replacement", "string", "count"),
    DIRECT_WHOLE_MATCH_TEMPLATE_REPLACEMENT_CASES,
)
def test_source_package_pattern_whole_match_template_replacement_matches_cpython(
    pattern: str,
    replacement: str,
    string: str,
    count: int,
) -> None:
    _assert_pattern_replacement_parity(pattern, replacement, string, count)


def test_source_package_literal_replacement_helpers_reject_string_bytes_mismatch() -> None:
    with pytest.raises(TypeError) as string_pattern_error:
        rebar.sub("abc", "x", b"abc")

    assert str(string_pattern_error.value) == (
        "cannot use a string pattern on a bytes-like object"
    )

    with pytest.raises(TypeError) as bytes_pattern_error:
        rebar.sub(b"abc", b"x", "abc")

    assert str(bytes_pattern_error.value) == (
        "cannot use a bytes pattern on a string-like object"
    )

    with pytest.raises(
        TypeError,
        match=re.escape("expected str instance, bytes found"),
    ):
        rebar.sub("abc", b"x", "abc")

    bytes_pattern = rebar.compile(b"abc")
    with pytest.raises(
        TypeError,
        match=re.escape("expected a bytes-like object, str found"),
    ):
        bytes_pattern.sub("x", b"abc")


def test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation(
) -> None:
    with pytest.raises(NotImplementedError) as module_template:
        rebar.sub("abc", r"\1", "abc")

    _assert_placeholder_message(
        module_template.value,
        "rebar.sub() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}

    with pytest.raises(NotImplementedError) as module_flags:
        rebar.subn("abc", "x", "abc", flags=rebar.IGNORECASE)

    _assert_placeholder_message(
        module_flags.value,
        "rebar.subn() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}

    with pytest.raises(NotImplementedError) as module_meta:
        rebar.sub("[ab]c", "x", "abc")

    _assert_placeholder_message(
        module_meta.value,
        "rebar.compile() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}

    with pytest.raises(NotImplementedError) as module_empty:
        rebar.sub("", "x", "abc")

    _assert_placeholder_message(
        module_empty.value,
        "rebar.sub() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}


def test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases(
) -> None:
    flagged_pattern = rebar.compile("abc", rebar.IGNORECASE)
    with pytest.raises(NotImplementedError) as bound_flags:
        flagged_pattern.sub("x", "abc")

    _assert_placeholder_message(
        bound_flags.value,
        "rebar.Pattern.sub() is a scaffold placeholder",
    )

    empty_pattern = rebar.compile("")
    with pytest.raises(NotImplementedError) as bound_empty:
        empty_pattern.subn("x", "abc")

    _assert_placeholder_message(
        bound_empty.value,
        "rebar.Pattern.subn() is a scaffold placeholder",
    )

    with pytest.raises(NotImplementedError) as bound_template:
        rebar.compile("abc").sub(r"\1", "abc")

    _assert_placeholder_message(
        bound_template.value,
        "rebar.Pattern.sub() is a scaffold placeholder",
    )
