from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
import re

import pytest

import rebar

from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    CORRECTNESS_FIXTURES_ROOT,
    CpythonReAdapter,
    FixtureCase,
    GROUPED_REPLACEMENT_FIXTURE_SELECTOR,
    NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR,
    NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
    RebarAdapter,
    evaluate_case,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    IndexLike as _IndexLike,
    IndexLikeBoomError as _IndexLikeBoomError,
    RecordingIndexLike as _RecordingIndexLike,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_mixed_text_model_case_pairs,
    assert_placeholder_message_contains,
    assert_valid_match_group_access_parity,
    build_selected_fixture_bundle,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    published_fixture_bundles_by_manifest_id,
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
GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID = "collection-replacement-workflows"
GROUPED_REPLACEMENT_NAMED_MANIFEST_ID = "named-group-replacement-workflows"
GROUPED_REPLACEMENT_GROUPED_ALTERNATION_MANIFEST_ID = (
    "grouped-alternation-replacement-workflows"
)
GROUPED_REPLACEMENT_NESTED_GROUP_MANIFEST_ID = "nested-group-replacement-workflows"
GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID = (
    "nested-group-alternation-replacement-workflows"
)
GROUPED_REPLACEMENT_QUANTIFIED_NESTED_GROUP_MANIFEST_ID = (
    "quantified-nested-group-replacement-workflows"
)
NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID = (
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
    "branch-local-backreference-replacement-workflows"
)
NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID = (
    "nested-broader-range-open-ended-quantified-group-alternation-"
    "branch-local-backreference-conditional-replacement-workflows"
)
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
GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID = "grouped-replacement-template"
OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE_ID = (
    "open-ended-quantified-group-replacement"
)
GROUPED_TEMPLATE_CALLABLE_CASE_ID = "module-sub-callable-str"
GROUPED_TEMPLATE_SELECTED_CASE_ID = "module-sub-grouping-template"
GROUPED_REPLACEMENT_COLLECTION_PATTERNS = frozenset({"abc", "(abc)"})
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
    "abc",
    rb"a((b|c){1,4})\2d",
    rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
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
    pytest.param(b"abc", b"x", b"zzz", 0, id="bytes-no-match"),
    pytest.param(b"abc", b"x", b"abcabc", 0, id="bytes-repeated-match"),
    pytest.param(b"abc", b"x", b"abcabc", 1, id="bytes-count-one"),
    pytest.param(b"abc", b"x", b"zabczz", 0, id="bytes-single-match"),
]
PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS = (
    "module-sub-str-no-match",
    "module-sub-str-single-match",
    "module-sub-str-repeated",
    "module-sub-bytes-no-match",
    "module-subn-bytes-count",
    "module-subn-bytes-repeated",
)
PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS = (
    "pattern-sub-str-no-match",
    "pattern-sub-str-single-match",
    "pattern-subn-str-count",
    "pattern-subn-str-repeated",
    "pattern-sub-bytes-no-match",
    "pattern-sub-bytes-single-match",
    "pattern-subn-bytes-count",
    "pattern-subn-bytes-repeated",
)
DIRECT_WHOLE_MATCH_TEMPLATE_REPLACEMENT_CASES = [
    pytest.param("abc", r"\g<0>x", "abc", 0, id="single-match"),
    pytest.param("abc", r"\g<0>x", "abcabc", 0, id="repeated-matches"),
    pytest.param("abc", r"\g<0>x", "abcabc", 1, id="count-one"),
]
_LITERAL_REPLACEMENT_MATRIX_PATTERNS = ("a", "ab", "ba")
_LITERAL_REPLACEMENT_MATRIX_REPLACEMENTS = ("", "x", "zz")
_LITERAL_REPLACEMENT_MATRIX_STRINGS = (
    "",
    "a",
    "aa",
    "aba",
    "abba",
    "baab",
    "ababab",
)
_LITERAL_REPLACEMENT_MATRIX_COUNTS = (0, 1, 2, -1)
_LITERAL_REPLACEMENT_HELPERS = ("sub", "subn")
_LITERAL_REPLACEMENT_COUNT_COERCION_CASES = (
    pytest.param("abc", "x", "abcabcabc", id="str"),
    pytest.param(b"abc", b"x", b"abcabcabc", id="bytes"),
)


_INDEXLIKE_ZERO = _IndexLike(0)
_INDEXLIKE_ONE = _IndexLike(1)
_INDEXLIKE_TWO = _IndexLike(2)
_LITERAL_REPLACEMENT_COUNT_COERCION_VALUES = (
    pytest.param(False, id="bool-false"),
    pytest.param(True, id="bool-true"),
    pytest.param(_INDEXLIKE_ZERO, id="indexlike-zero"),
    pytest.param(_INDEXLIKE_ONE, id="indexlike-one"),
    pytest.param(_INDEXLIKE_TWO, id="indexlike-two"),
)


def _literal_replacement_matrix_payloads(
    text_model: str,
) -> tuple[tuple[TextValue, ...], tuple[TextValue, ...], tuple[TextValue, ...]]:
    if text_model == "bytes":
        return (
            tuple(
                pattern.encode("ascii")
                for pattern in _LITERAL_REPLACEMENT_MATRIX_PATTERNS
            ),
            tuple(
                replacement.encode("ascii")
                for replacement in _LITERAL_REPLACEMENT_MATRIX_REPLACEMENTS
            ),
            tuple(
                string.encode("ascii")
                for string in _LITERAL_REPLACEMENT_MATRIX_STRINGS
            ),
        )
    return (
        _LITERAL_REPLACEMENT_MATRIX_PATTERNS,
        _LITERAL_REPLACEMENT_MATRIX_REPLACEMENTS,
        _LITERAL_REPLACEMENT_MATRIX_STRINGS,
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
class InvalidExpandTemplateCase:
    case_id: str
    pattern: TextValue
    string: TextValue
    template: TextValue
    use_compiled_pattern: bool


INVALID_EXPAND_TEMPLATE_CASES = (
    InvalidExpandTemplateCase(
        case_id="module-str-missing-named-group",
        pattern="(?P<word>abc)",
        string="abc",
        template=r"<\g<missing>>",
        use_compiled_pattern=False,
    ),
    InvalidExpandTemplateCase(
        case_id="module-str-invalid-numbered-group",
        pattern="(abc)",
        string="abc",
        template=r"\2",
        use_compiled_pattern=False,
    ),
    InvalidExpandTemplateCase(
        case_id="compiled-str-missing-named-group",
        pattern="(?P<word>abc)",
        string="abc",
        template=r"<\g<missing>>",
        use_compiled_pattern=True,
    ),
    InvalidExpandTemplateCase(
        case_id="compiled-str-invalid-numbered-group",
        pattern="(abc)",
        string="abc",
        template=r"\2",
        use_compiled_pattern=True,
    ),
)


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
    pattern_extractor: Callable[[FixtureCase], TextValue]
    compile_patterns: tuple[TextValue, ...] = ()
    match_snapshot_manifest_ids: tuple[str, ...] = ()
    match_group_access_manifest_ids: tuple[str, ...] = ()
    template_expand_manifest_ids: tuple[str, ...] = ()
    fixture_selector: str | None = None
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


def _compiled_case_pattern(case: FixtureCase) -> re.Pattern[str] | re.Pattern[bytes]:
    return re.compile(case_pattern(case), case.flags or 0)


def _grouped_replacement_group_kind(case: FixtureCase) -> str:
    return "named" if _compiled_case_pattern(case).groupindex else "numbered"


def _expected_grouped_replacement_template(case: FixtureCase) -> TextValue:
    compiled = _compiled_case_pattern(case)
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
        template = f"<{replacement}>"
    elif compiled.groupindex and compiled.pattern in {r"(?P<word>abc)", br"(?P<word>abc)"}:
        template = f"<{replacement}>"
    else:
        template = f"{replacement}x"
    if case.text_model == "bytes":
        return template.encode("latin-1")
    return template


def _assert_grouped_replacement_fixture_bundle_contract(bundle: FixtureBundle) -> None:
    text_models = {case.text_model for case in bundle.cases}
    expected_group_kind_counts = (
        GROUPED_REPLACEMENT_NESTED_ALTERNATION_GROUP_KIND_COUNTS
        if bundle.expected_manifest_id == "nested-group-alternation-replacement-workflows"
        else GROUPED_REPLACEMENT_SHARED_GROUP_KIND_COUNTS
    )
    expected_group_kind_counts = Counter(
        {
            key: value * len(text_models)
            for key, value in expected_group_kind_counts.items()
        }
    )
    assert Counter(
        (case.operation, case.helper, _grouped_replacement_group_kind(case))
        for case in bundle.cases
    ) == expected_group_kind_counts

    for case in bundle.cases:
        compiled = _compiled_case_pattern(case)
        count_index = 3 if case.operation == "module_call" else 2

        assert case.kwargs == {}
        assert "replacement-template" in case.categories
        assert case.text_model in {"str", "bytes"}
        assert case.text_model in case.categories
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


def _grouped_replacement_collection_case_ids(
    bundle: FixtureBundle,
) -> tuple[str, ...]:
    return tuple(
        case.case_id
        for case in bundle.cases
        if case.family == "grouped_template_replacement_workflow"
        or "callable-replacement" in case.categories
    )


def _load_surface(spec: ReplacementSurfaceSpec) -> LoadedReplacementSurface:
    if spec.fixture_selector is None:
        raise ValueError(f"{spec.id} is missing a published fixture selector")
    bundles = tuple(
        build_selected_fixture_bundle(
            path,
            pattern_extractor=spec.pattern_extractor,
        )
        for path in select_correctness_fixture_paths(spec.fixture_selector)
    )
    bundles_by_manifest_id = published_fixture_bundles_by_manifest_id(bundles)
    if spec.id == GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID:
        collection_bundle = bundles_by_manifest_id[GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID]
        selected_collection_case_ids = _grouped_replacement_collection_case_ids(
            collection_bundle
        )
        selected_collection_case_id_set = frozenset(selected_collection_case_ids)
        adjusted_collection_bundle = build_selected_fixture_bundle(
            collection_bundle.manifest.path,
            selected_case_ids=selected_collection_case_ids,
            pattern_extractor=spec.pattern_extractor,
            expected_text_models=frozenset(
                case.text_model or "str"
                for case in collection_bundle.cases
                if case.case_id in selected_collection_case_id_set
            ),
        )
        adjusted_bundles = tuple(
            adjusted_collection_bundle
            if (
                bundle.expected_manifest_id
                == GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID
            )
            else bundle
            for bundle in bundles
        )
        adjusted_bundles_by_manifest_id = published_fixture_bundles_by_manifest_id(
            adjusted_bundles
        )
        bundles = tuple(
            adjusted_bundles_by_manifest_id[manifest_id]
            for manifest_id in (
                GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID,
                GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,
                GROUPED_REPLACEMENT_GROUPED_ALTERNATION_MANIFEST_ID,
                GROUPED_REPLACEMENT_NESTED_GROUP_MANIFEST_ID,
                GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID,
                GROUPED_REPLACEMENT_QUANTIFIED_NESTED_GROUP_MANIFEST_ID,
                NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
            )
        )
    if spec.id == OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE_ID:
        loaded_manifest_ids = frozenset(
            bundle.expected_manifest_id for bundle in bundles
        )
        expected_manifest_ids = frozenset(spec.template_expand_manifest_ids)
        if loaded_manifest_ids != expected_manifest_ids:
            raise ValueError(
                "bundle manifest ids drifted: "
                f"{tuple(sorted(loaded_manifest_ids))!r} != "
                f"{tuple(sorted(expected_manifest_ids))!r}"
            )
        bundles_by_manifest_id = published_fixture_bundles_by_manifest_id(bundles)
        bundles = tuple(
            bundles_by_manifest_id[manifest_id]
            for manifest_id in spec.template_expand_manifest_ids
        )
    published_replacement_cases = tuple(
        case for bundle in bundles for case in bundle.cases
    )
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
        template_expand_cases=tuple(
            case
            for case in _cases_for_manifest_ids(
                replacement_cases,
                spec.template_expand_manifest_ids,
            )
            if "replacement-template" in case.categories
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
        pattern_extractor=case_pattern,
        compile_patterns=GROUPED_REPLACEMENT_COMPILE_PATTERNS,
        match_group_access_manifest_ids=(GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,),
        template_expand_manifest_ids=(
            GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID,
            GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,
            GROUPED_REPLACEMENT_GROUPED_ALTERNATION_MANIFEST_ID,
            GROUPED_REPLACEMENT_NESTED_GROUP_MANIFEST_ID,
            GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID,
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
        ),
        fixture_selector=GROUPED_REPLACEMENT_FIXTURE_SELECTOR,
        supplemental_no_match_cases=GROUPED_REPLACEMENT_SUPPLEMENTAL_NO_MATCH_CASES,
        supplemental_repeated_cases=GROUPED_REPLACEMENT_SUPPLEMENTAL_REPEATED_CASES,
    ),
    ReplacementSurfaceSpec(
        id="open-ended-quantified-group-replacement",
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
        fixture_selector=OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
        supplemental_no_match_cases=OPEN_ENDED_SUPPLEMENTAL_NO_MATCH_CASES,
        supplemental_repeated_cases=OPEN_ENDED_SUPPLEMENTAL_REPEATED_CASES,
    ),
    ReplacementSurfaceSpec(
        id="conditional-group-exists-replacement",
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
        fixture_selector=CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
        discover_no_match_on_all_replacement_cases=True,
        no_match_text_candidates=NO_MATCH_TEXT_CANDIDATES,
        supplemental_repeated_cases=CONDITIONAL_SUPPLEMENTAL_REPEATED_CASES,
    ),
)
REPLACEMENT_SURFACES = tuple(
    _load_surface(spec) for spec in REPLACEMENT_SURFACE_SPECS
)


def _replacement_surface_by_id(surface_id: str) -> LoadedReplacementSurface:
    for surface in REPLACEMENT_SURFACES:
        if surface.spec.id == surface_id:
            return surface
    raise AssertionError(f"unknown replacement surface {surface_id!r}")


def _grouped_replacement_contract_bundles(
    surface: LoadedReplacementSurface,
) -> tuple[FixtureBundle, ...]:
    assert surface.spec.id == GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID
    return surface.bundles[2:]


GROUPED_REPLACEMENT_TEMPLATE_SURFACE = _replacement_surface_by_id(
    GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID
)
OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE = _replacement_surface_by_id(
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE_ID
)
OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_BUNDLES_BY_MANIFEST_ID = (
    published_fixture_bundles_by_manifest_id(
        OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE.bundles
    )
)
MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE = (
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_BUNDLES_BY_MANIFEST_ID[
        NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID
    ]
)
BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE = (
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_BUNDLES_BY_MANIFEST_ID[
        NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID
    ]
)
GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID = (
    published_fixture_bundles_by_manifest_id(
        GROUPED_REPLACEMENT_TEMPLATE_SURFACE.bundles
    )
)
BROADER_RANGE_WIDER_RANGED_REPEAT_MIXED_TEXT_REPLACEMENT_BUNDLE = (
    GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID
    ]
)

def _selector_surface_params() -> tuple[object, ...]:
    return tuple(
        pytest.param(surface, id=surface.spec.id)
        for surface in REPLACEMENT_SURFACES
        if surface.spec.fixture_selector is not None
    )


def _bundle_params() -> tuple[object, ...]:
    return tuple(
        pytest.param(surface, bundle, id=bundle.expected_manifest_id)
        for surface in REPLACEMENT_SURFACES
        for bundle in surface.bundles
    )


def _compile_pattern_params() -> tuple[object, ...]:
    return tuple(
        pytest.param(surface, pattern, id=_pattern_param_id(pattern))
        for surface in REPLACEMENT_SURFACES
        for pattern in surface.spec.compile_patterns
    )


def _replacement_case_params(
    case_selector: Callable[[LoadedReplacementSurface], tuple[FixtureCase, ...]],
    *,
    include_surface: bool = False,
    case_transform: Callable[[FixtureCase], object] | None = None,
) -> tuple[object, ...]:
    params: list[object] = []
    for surface in REPLACEMENT_SURFACES:
        for case in case_selector(surface):
            param_case = case if case_transform is None else case_transform(case)
            if include_surface:
                params.append(pytest.param(surface, param_case, id=case.case_id))
            else:
                params.append(pytest.param(param_case, id=case.case_id))
    return tuple(params)


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


def _assert_mixed_text_replacement_surface_loader_contract(
    *,
    spec: ReplacementSurfaceSpec,
    manifest_id: str,
) -> tuple[LoadedReplacementSurface, tuple[str, ...]]:
    surface = _load_surface(spec)
    (bundle,) = surface.bundles
    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)
    str_case_ids = tuple(case.case_id for case in str_cases)
    bytes_case_ids = tuple(case.case_id for case in bytes_cases)
    all_case_ids = tuple(case.case_id for case in bundle.cases)
    selected_case_ids = (
        str_case_ids
        if manifest_id in spec.pending_bytes_follow_on_manifest_ids
        else all_case_ids
    )
    selected_case_id_set = frozenset(selected_case_ids)
    uncovered_case_ids = (
        bytes_case_ids
        if manifest_id in spec.pending_bytes_follow_on_manifest_ids
        else ()
    )
    expected_operation_helper_counts = (
        EXPECTED_OPERATION_HELPER_COUNTS
        if uncovered_case_ids
        else MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    )
    module_case_ids = tuple(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "module_call")
        if case.case_id in selected_case_id_set
    )
    pattern_case_ids = tuple(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
        if case.case_id in selected_case_id_set
    )

    assert len(bundle.cases) == 16
    assert len(str_case_ids) == 8
    assert len(bytes_case_ids) == 8
    assert tuple(case.case_id for case in (*str_cases, *bytes_cases)) == all_case_ids
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    )
    assert tuple(case.case_id for case in surface.replacement_cases) == (
        selected_case_ids
    )
    assert Counter((case.operation, case.helper) for case in surface.replacement_cases) == (
        expected_operation_helper_counts
    )
    assert tuple(case.case_id for case in surface.module_cases) == module_case_ids
    assert tuple(case.case_id for case in surface.pattern_cases) == pattern_case_ids
    assert _expected_selected_replacement_case_ids(
        surface,
        manifest_id=manifest_id,
    ) == selected_case_ids
    assert _expected_uncovered_replacement_case_ids(
        surface,
        manifest_id,
    ) == uncovered_case_ids
    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=selected_case_ids,
        expected_uncovered_case_ids=uncovered_case_ids,
    )
    return surface, selected_case_ids


@pytest.mark.parametrize("surface", _selector_surface_params())
def test_replacement_parity_suite_tracks_published_fixture_coverage_frontier(
    surface: LoadedReplacementSurface,
) -> None:
    assert surface.spec.fixture_selector is not None
    selector_fixture_paths = select_correctness_fixture_paths(
        surface.spec.fixture_selector
    )

    covered_path_set = {bundle.manifest.path for bundle in surface.bundles}
    covered_paths = tuple(
        path
        for path in selector_fixture_paths
        if path in covered_path_set
    )
    uncovered_paths = tuple(
        path
        for path in selector_fixture_paths
        if path not in covered_path_set
    )
    assert covered_paths
    assert covered_path_set == set(covered_paths)
    assert tuple(path.name for path in uncovered_paths) == (
        surface.spec.known_uncovered_published_fixture_filenames
    )
    assert set((*covered_paths, *uncovered_paths)) == set(selector_fixture_paths)


@pytest.mark.parametrize(("surface", "bundle"), _bundle_params())
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    surface: LoadedReplacementSurface,
    bundle: FixtureBundle,
) -> None:
    pattern_extractor = (
        case_pattern
        if bundle.expected_text_models == MIXED_TEXT_MODELS
        else surface.spec.pattern_extractor
    )
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=pattern_extractor,
    )
    if (
        surface.spec.id == GROUPED_REPLACEMENT_TEMPLATE_SURFACE_ID
        and bundle in _grouped_replacement_contract_bundles(surface)
    ):
        _assert_grouped_replacement_fixture_bundle_contract(bundle)


def test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit() -> None:
    surface = GROUPED_REPLACEMENT_TEMPLATE_SURFACE

    assert tuple(bundle.expected_manifest_id for bundle in surface.bundles) == (
        GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID,
        GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,
        GROUPED_REPLACEMENT_GROUPED_ALTERNATION_MANIFEST_ID,
        GROUPED_REPLACEMENT_NESTED_GROUP_MANIFEST_ID,
        GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID,
        GROUPED_REPLACEMENT_QUANTIFIED_NESTED_GROUP_MANIFEST_ID,
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
    )
    assert tuple(
        bundle.expected_manifest_id
        for bundle in _grouped_replacement_contract_bundles(surface)
    ) == (
        GROUPED_REPLACEMENT_GROUPED_ALTERNATION_MANIFEST_ID,
        GROUPED_REPLACEMENT_NESTED_GROUP_MANIFEST_ID,
        GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID,
        GROUPED_REPLACEMENT_QUANTIFIED_NESTED_GROUP_MANIFEST_ID,
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID,
    )

    grouped_template_bundle = surface.bundles[0]
    grouped_template_case_ids = _grouped_replacement_collection_case_ids(
        grouped_template_bundle
    )
    assert tuple(case.case_id for case in grouped_template_bundle.cases) == (
        grouped_template_case_ids
    )
    assert grouped_template_case_ids == (
        GROUPED_TEMPLATE_CALLABLE_CASE_ID,
        GROUPED_TEMPLATE_SELECTED_CASE_ID,
    )
    grouped_template_case = next(
        case
        for case in grouped_template_bundle.cases
        if case.case_id == GROUPED_TEMPLATE_SELECTED_CASE_ID
    )
    assert grouped_template_case.operation == "module_call"
    assert grouped_template_case.helper == "sub"
    assert str_case_pattern(grouped_template_case) == "(abc)"
    assert case_replacement_argument(grouped_template_case) == r"\1x"
    assert case_text_argument(grouped_template_case) == "abc"
    assert "replacement-template" in grouped_template_case.categories
    assert "grouping-dependent" in grouped_template_case.categories

    named_bundle = GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
        GROUPED_REPLACEMENT_NAMED_MANIFEST_ID
    ]
    named_case_ids = _expected_selected_replacement_case_ids(
        surface,
        manifest_id=GROUPED_REPLACEMENT_NAMED_MANIFEST_ID,
    )
    assert tuple(case.case_id for case in named_bundle.cases) == named_case_ids
    assert named_case_ids == (
        "module-sub-template-named-group-str",
        "module-subn-template-named-group-str",
        "pattern-sub-template-named-group-str",
        "pattern-subn-template-named-group-str",
    )
    for case in named_bundle.cases:
        assert case_replacement_argument(case) == r"<\g<word>>"
        assert "named-group" in case.categories
        assert "replacement-template" in case.categories
        assert case.text_model == "str"

    nested_group_alternation_bundle = GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
        GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID
    ]
    nested_group_alternation_case_ids = _expected_selected_replacement_case_ids(
        surface,
        manifest_id=GROUPED_REPLACEMENT_NESTED_GROUP_ALTERNATION_MANIFEST_ID,
    )
    assert tuple(case.case_id for case in nested_group_alternation_bundle.cases) == (
        nested_group_alternation_case_ids
    )
    assert nested_group_alternation_case_ids == (
        "module-sub-template-nested-group-alternation-numbered-outer-str",
        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
        "module-sub-template-nested-group-alternation-numbered-wrapper-str",
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    )
    assert {
        case.case_id
        for case in nested_group_alternation_bundle.cases
        if "wrapper-template" in case.categories
    } == {
        "module-sub-template-nested-group-alternation-numbered-wrapper-str",
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    }


def test_bundle_pattern_projection_and_case_source_payloads_cover_published_fixtures(
) -> None:
    bundle = GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
        GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID
    ]
    cases_by_id = {case.case_id: case for case in bundle.cases}
    selected_case_ids = _grouped_replacement_collection_case_ids(bundle)

    assert tuple(case.case_id for case in bundle.cases) == selected_case_ids
    assert selected_case_ids == (
        GROUPED_TEMPLATE_CALLABLE_CASE_ID,
        GROUPED_TEMPLATE_SELECTED_CASE_ID,
    )
    assert {case_pattern(case) for case in bundle.cases} == (
        GROUPED_REPLACEMENT_COLLECTION_PATTERNS
    )
    assert {str_case_pattern(case) for case in bundle.cases} == (
        GROUPED_REPLACEMENT_COLLECTION_PATTERNS
    )
    assert cases_by_id[GROUPED_TEMPLATE_CALLABLE_CASE_ID].source_args[1] == {
        "type": "callable_constant",
        "value": "x",
    }
    assert cases_by_id[GROUPED_TEMPLATE_CALLABLE_CASE_ID].source_kwargs == {}
    assert cases_by_id[GROUPED_TEMPLATE_SELECTED_CASE_ID].source_args[1] == r"\1x"
    assert cases_by_id[GROUPED_TEMPLATE_SELECTED_CASE_ID].source_kwargs == {}


def test_case_argument_helpers_cover_module_and_pattern_replacement_rows() -> None:
    module_bundle = GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
        GROUPED_REPLACEMENT_COLLECTION_MANIFEST_ID
    ]
    named_bundle = GROUPED_REPLACEMENT_TEMPLATE_BUNDLES_BY_MANIFEST_ID[
        GROUPED_REPLACEMENT_NAMED_MANIFEST_ID
    ]

    module_case = next(
        case
        for case in module_bundle.cases
        if case.case_id == GROUPED_TEMPLATE_SELECTED_CASE_ID
    )
    pattern_case = next(
        case
        for case in named_bundle.cases
        if case.case_id == "pattern-sub-template-named-group-str"
    )

    assert case_replacement_argument(module_case) == module_case.args[1]
    assert case_text_argument(module_case) == module_case.args[2]
    assert case_replacement_argument(pattern_case) == pattern_case.args[0]
    assert case_text_argument(pattern_case) == pattern_case.args[1]


@pytest.mark.parametrize(("surface", "bundle"), _bundle_params())
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


@pytest.mark.parametrize("surface", _selector_surface_params())
def test_replacement_direct_test_buckets_cover_selected_frontier(
    surface: LoadedReplacementSurface,
) -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "module": frozenset(case.case_id for case in surface.module_cases),
            "pattern": frozenset(case.case_id for case in surface.pattern_cases),
        },
        selected_case_ids=_expected_selected_replacement_case_ids(surface),
        coverage_label=f"{surface.spec.id} replacement direct-test case-id buckets",
    )


def test_replacement_frontier_has_no_live_unimplemented_cases() -> None:
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()
    live_unimplemented_case_ids = tuple(
        case.case_id
        for surface in REPLACEMENT_SURFACES
        for case in surface.replacement_cases
        if evaluate_case(case, cpython_adapter, rebar_adapter)["comparison"]
        == "unimplemented"
    )

    assert live_unimplemented_case_ids == ()


def test_mixed_replacement_manifest_routes_bytes_rows_through_shared_parity_surface(
) -> None:
    bundle = MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE
    surface = OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE
    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)
    str_case_ids = frozenset(case.case_id for case in str_cases)
    bytes_case_ids = frozenset(case.case_id for case in bytes_cases)
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

    assert shared_module_case_ids == expected_module_case_ids
    assert shared_pattern_case_ids == expected_pattern_case_ids
    assert shared_match_group_access_case_ids == str_case_ids | bytes_case_ids
    assert shared_template_expand_case_ids == str_case_ids | bytes_case_ids


def test_broader_range_open_ended_replacement_manifest_routes_bytes_rows_through_shared_parity_surface(
) -> None:
    bundle = BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE
    surface = OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_SURFACE
    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)
    ordered_str_case_ids = tuple(case.case_id for case in str_cases)
    ordered_bytes_case_ids = tuple(case.case_id for case in bytes_cases)
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

    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    )
    assert shared_module_case_ids == expected_module_case_ids
    assert shared_pattern_case_ids == expected_pattern_case_ids
    assert shared_template_expand_case_ids == (
        frozenset(ordered_str_case_ids) | frozenset(ordered_bytes_case_ids)
    )


def test_broader_range_wider_ranged_repeat_replacement_manifest_keeps_mixed_text_on_shared_parity_surface(
) -> None:
    manifest_id = NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_REPLACEMENT_MANIFEST_ID
    bundle = BROADER_RANGE_WIDER_RANGED_REPEAT_MIXED_TEXT_REPLACEMENT_BUNDLE
    surface = GROUPED_REPLACEMENT_TEMPLATE_SURFACE
    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)
    ordered_str_case_ids = tuple(case.case_id for case in str_cases)
    ordered_bytes_case_ids = tuple(case.case_id for case in bytes_cases)
    expected_selected_case_ids = _expected_selected_replacement_case_ids(
        surface,
        manifest_id=manifest_id,
    )
    expected_module_case_ids = tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), "module_call")
    )
    expected_pattern_case_ids = tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), "pattern_call")
    )

    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    )
    assert tuple(case.case_id for case in bundle.cases) == expected_selected_case_ids
    assert tuple(
        case.case_id
        for case in surface.replacement_cases
        if case.manifest_id == manifest_id
    ) == expected_selected_case_ids
    assert tuple(
        case.case_id for case in surface.module_cases if case.manifest_id == manifest_id
    ) == expected_module_case_ids
    assert tuple(
        case.case_id for case in surface.pattern_cases if case.manifest_id == manifest_id
    ) == expected_pattern_case_ids
    assert tuple(
        case.case_id
        for case in surface.template_expand_cases
        if case.manifest_id == manifest_id
    ) == expected_selected_case_ids
    assert _expected_selected_replacement_case_ids(
        surface,
        manifest_id=manifest_id,
    ) == expected_selected_case_ids
    assert _expected_uncovered_replacement_case_ids(
        surface,
        manifest_id,
    ) == ()
    assert_fixture_bundle_tracks_published_case_frontier(
        bundle,
        selected_case_ids=expected_selected_case_ids,
        expected_uncovered_case_ids=(),
    )


def test_broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on(
) -> None:
    manifest_id = NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID
    surface, selected_case_ids = _assert_mixed_text_replacement_surface_loader_contract(
        spec=ReplacementSurfaceSpec(
            id="broader-range-open-ended-replacement-pending-bytes-contract",
            fixture_selector=NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
            pattern_extractor=case_pattern,
            template_expand_manifest_ids=(manifest_id,),
            pending_bytes_follow_on_manifest_ids=frozenset({manifest_id}),
        ),
        manifest_id=manifest_id,
    )

    assert tuple(case.case_id for case in surface.match_group_access_cases) == ()
    assert tuple(case.case_id for case in surface.template_expand_cases) == (
        selected_case_ids
    )


def test_mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on() -> None:
    manifest_id = NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID
    surface, selected_case_ids = _assert_mixed_text_replacement_surface_loader_contract(
        spec=ReplacementSurfaceSpec(
            id="mixed-replacement-pending-bytes-contract",
            fixture_selector=(
                NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR
            ),
            pattern_extractor=case_pattern,
            match_group_access_manifest_ids=(manifest_id,),
            template_expand_manifest_ids=(manifest_id,),
            pending_bytes_follow_on_manifest_ids=frozenset({manifest_id}),
        ),
        manifest_id=manifest_id,
    )

    assert tuple(case.case_id for case in surface.match_group_access_cases) == (
        selected_case_ids
    )
    assert tuple(case.case_id for case in surface.template_expand_cases) == (
        selected_case_ids
    )


def test_broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier(
) -> None:
    manifest_id = NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID
    surface, selected_case_ids = _assert_mixed_text_replacement_surface_loader_contract(
        spec=ReplacementSurfaceSpec(
            id="broader-range-open-ended-replacement-mixed-contract",
            fixture_selector=NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
            pattern_extractor=case_pattern,
            template_expand_manifest_ids=(manifest_id,),
        ),
        manifest_id=manifest_id,
    )

    assert tuple(case.case_id for case in surface.match_group_access_cases) == ()
    assert tuple(case.case_id for case in surface.template_expand_cases) == (
        selected_case_ids
    )


@pytest.mark.parametrize(("surface", "pattern"), _compile_pattern_params())
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    surface: LoadedReplacementSurface,
    pattern: TextValue,
) -> None:
    del surface
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, pattern)


@pytest.mark.parametrize(
    "case",
    _replacement_case_params(
        lambda surface: surface.module_cases,
        case_transform=_replacement_parity_case,
    ),
)
def test_module_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize(
    "case",
    _replacement_case_params(
        lambda surface: surface.pattern_cases,
        case_transform=_replacement_parity_case,
    ),
)
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


@pytest.mark.parametrize(
    ("surface", "case"),
    _replacement_case_params(
        lambda surface: surface.match_snapshot_cases,
        include_surface=True,
    ),
)
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


@pytest.mark.parametrize(
    ("surface", "case"),
    _replacement_case_params(
        lambda surface: surface.match_group_access_cases,
        include_surface=True,
    ),
)
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


@pytest.mark.parametrize(
    ("surface", "case"),
    _replacement_case_params(
        lambda surface: surface.match_group_access_cases,
        include_surface=True,
    ),
)
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


@pytest.mark.parametrize(
    ("surface", "case"),
    _replacement_case_params(
        lambda surface: surface.template_expand_cases,
        include_surface=True,
    ),
)
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


@pytest.mark.parametrize(
    "case",
    INVALID_EXPAND_TEMPLATE_CASES,
    ids=lambda case: case.case_id,
)
def test_replacement_template_match_expand_invalid_templates_match_cpython(
    regex_backend: tuple[str, object],
    case: InvalidExpandTemplateCase,
) -> None:
    backend_name, backend = regex_backend

    if case.use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
        )
        observed_match = observed_pattern.search(case.string)
        expected_match = expected_pattern.search(case.string)
    else:
        observed_match = backend.search(case.pattern, case.string)
        expected_match = re.search(case.pattern, case.string)

    assert_match_parity(
        backend_name,
        observed_match,
        expected_match,
        check_regs=True,
    )
    assert observed_match is not None
    assert expected_match is not None
    assert_match_convenience_api_parity(observed_match, expected_match)

    observed_error = _capture_exception(lambda: observed_match.expand(case.template))
    expected_error = _capture_exception(lambda: expected_match.expand(case.template))

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize(
    ("surface", "case"),
    _replacement_case_params(
        lambda surface: surface.discovered_no_match_cases,
        include_surface=True,
    ),
)
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


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for surface in REPLACEMENT_SURFACES
        for case in surface.spec.supplemental_no_match_cases
    ),
)
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


@pytest.mark.parametrize(
    "case",
    tuple(
        pytest.param(case, id=case.id)
        for surface in REPLACEMENT_SURFACES
        for case in surface.spec.supplemental_repeated_cases
    ),
)
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


@pytest.mark.parametrize(
    "case",
    tuple(pytest.param(case, id=case.id) for case in SUPPLEMENTAL_NEGATIVE_COUNT_CASES),
)
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
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT
        / "open_ended_quantified_group_alternation_workflows.py",
        pattern_extractor=case_pattern,
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


def _assert_literal_replacement_result_matches_cpython(
    *,
    backend_name: str,
    context: str,
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: object,
    observed: ReplacementOutcome,
    expected: ReplacementOutcome,
) -> None:
    try:
        assert type(observed) is type(expected)
        assert observed == expected
    except AssertionError as exc:
        raise AssertionError(
            f"{backend_name} {context} {helper} mismatch for pattern={pattern!r}, "
            f"replacement={replacement!r}, string={string!r}, count={count!r}"
        ) from exc


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


def _assert_direct_literal_replacement_publication_contract(
    *,
    selected_case_ids: tuple[str, ...],
    operation: str,
    expected_args_by_case_id: dict[str, tuple[object, ...]],
    expected_helpers: tuple[str, ...],
    expected_text_models: tuple[str, ...],
) -> None:
    bundle = build_selected_fixture_bundle(
        CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py",
        selected_case_ids=selected_case_ids,
        pattern_extractor=case_pattern,
    )
    cases_by_id = {case.case_id: case for case in bundle.cases}

    assert tuple(case.case_id for case in bundle.cases) == selected_case_ids
    assert tuple(
        case.case_id for case in fixture_cases_for_operation((bundle,), operation)
    ) == selected_case_ids
    assert tuple(tuple(cases_by_id[case_id].args) for case_id in selected_case_ids) == (
        tuple(expected_args_by_case_id[case_id] for case_id in selected_case_ids)
    )
    assert tuple(cases_by_id[case_id].helper for case_id in selected_case_ids) == (
        expected_helpers
    )
    assert tuple(cases_by_id[case_id].text_model for case_id in selected_case_ids) == (
        expected_text_models
    )


def test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order(
) -> None:
    _assert_direct_literal_replacement_publication_contract(
        selected_case_ids=PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS,
        operation="module_call",
        expected_args_by_case_id={
            "module-sub-str-no-match": ("abc", "x", "zzz"),
            "module-sub-str-single-match": ("abc", "x", "zabczz"),
            "module-sub-str-repeated": ("abc", "x", "abcabc"),
            "module-sub-bytes-no-match": (b"abc", b"x", b"zzz"),
            "module-subn-bytes-count": (b"abc", b"x", b"abcabc", 1),
            "module-subn-bytes-repeated": (b"abc", b"x", b"abcabc"),
        },
        expected_helpers=("sub", "sub", "sub", "sub", "subn", "subn"),
        expected_text_models=("str", "str", "str", "bytes", "bytes", "bytes"),
    )


def test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order(
) -> None:
    _assert_direct_literal_replacement_publication_contract(
        selected_case_ids=PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS,
        operation="pattern_call",
        expected_args_by_case_id={
            "pattern-sub-str-no-match": ("x", "zzz"),
            "pattern-sub-str-single-match": ("x", "zabczz"),
            "pattern-subn-str-count": ("x", "abcabc", 1),
            "pattern-subn-str-repeated": ("x", "abcabc"),
            "pattern-sub-bytes-no-match": (b"x", b"zzz"),
            "pattern-sub-bytes-single-match": (b"x", b"zabczz"),
            "pattern-subn-bytes-count": (b"x", b"abcabc", 1),
            "pattern-subn-bytes-repeated": (b"x", b"abcabc"),
        },
        expected_helpers=("sub", "sub", "subn", "subn", "sub", "sub", "subn", "subn"),
        expected_text_models=(
            "str",
            "str",
            "str",
            "str",
            "bytes",
            "bytes",
            "bytes",
            "bytes",
        ),
    )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_replacement_matrix_module_helpers_match_cpython(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, replacements, strings = _literal_replacement_matrix_payloads(text_model)

    for pattern in patterns:
        for replacement in replacements:
            for string in strings:
                for count in _LITERAL_REPLACEMENT_MATRIX_COUNTS:
                    for helper in _LITERAL_REPLACEMENT_HELPERS:
                        _assert_literal_replacement_result_matches_cpython(
                            backend_name=backend_name,
                            context="module",
                            helper=helper,
                            pattern=pattern,
                            replacement=replacement,
                            string=string,
                            count=count,
                            observed=getattr(
                                backend,
                                helper,
                            )(pattern, replacement, string, count=count),
                            expected=getattr(
                                re,
                                helper,
                            )(pattern, replacement, string, count=count),
                        )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_replacement_matrix_pattern_helpers_match_cpython(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, replacements, strings = _literal_replacement_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for replacement in replacements:
            for string in strings:
                for count in _LITERAL_REPLACEMENT_MATRIX_COUNTS:
                    for helper in _LITERAL_REPLACEMENT_HELPERS:
                        _assert_literal_replacement_result_matches_cpython(
                            backend_name=backend_name,
                            context="pattern",
                            helper=helper,
                            pattern=pattern,
                            replacement=replacement,
                            string=string,
                            count=count,
                            observed=getattr(
                                observed_pattern,
                                helper,
                            )(replacement, string, count=count),
                            expected=getattr(
                                expected_pattern,
                                helper,
                            )(replacement, string, count=count),
                        )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_replacement_matrix_module_helpers_accept_compiled_patterns(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, replacements, strings = _literal_replacement_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for replacement in replacements:
            for string in strings:
                for count in _LITERAL_REPLACEMENT_MATRIX_COUNTS:
                    for helper in _LITERAL_REPLACEMENT_HELPERS:
                        _assert_literal_replacement_result_matches_cpython(
                            backend_name=backend_name,
                            context="compiled-pattern module",
                            helper=helper,
                            pattern=pattern,
                            replacement=replacement,
                            string=string,
                            count=count,
                            observed=getattr(
                                backend,
                                helper,
                            )(observed_pattern, replacement, string, count=count),
                            expected=getattr(
                                re,
                                helper,
                            )(expected_pattern, replacement, string, count=count),
                        )


# Keep the representative fixture-backed rows normalized to ints, then use a
# compact direct matrix here to prove replacement helpers accept bool and
# __index__ count carriers across all entry points.
@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("count", _LITERAL_REPLACEMENT_COUNT_COERCION_VALUES)
def test_literal_replacement_count_coercion_matches_cpython_for_module_helpers(
    regex_backend: tuple[str, object],
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: object,
) -> None:
    backend_name, backend = regex_backend

    for helper in _LITERAL_REPLACEMENT_HELPERS:
        _assert_literal_replacement_result_matches_cpython(
            backend_name=backend_name,
            context="module count coercion",
            helper=helper,
            pattern=pattern,
            replacement=replacement,
            string=string,
            count=count,
            observed=getattr(
                backend,
                helper,
            )(pattern, replacement, string, count=count),
            expected=getattr(
                re,
                helper,
            )(pattern, replacement, string, count=count),
        )


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("count", _LITERAL_REPLACEMENT_COUNT_COERCION_VALUES)
def test_literal_replacement_count_coercion_matches_cpython_for_pattern_helpers(
    regex_backend: tuple[str, object],
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: object,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )

    for helper in _LITERAL_REPLACEMENT_HELPERS:
        _assert_literal_replacement_result_matches_cpython(
            backend_name=backend_name,
            context="pattern count coercion",
            helper=helper,
            pattern=pattern,
            replacement=replacement,
            string=string,
            count=count,
            observed=getattr(
                observed_pattern,
                helper,
            )(replacement, string, count=count),
            expected=getattr(
                expected_pattern,
                helper,
            )(replacement, string, count=count),
        )


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("count", _LITERAL_REPLACEMENT_COUNT_COERCION_VALUES)
def test_literal_replacement_count_coercion_matches_cpython_for_compiled_pattern_module_helpers(
    regex_backend: tuple[str, object],
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
    count: object,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )

    for helper in _LITERAL_REPLACEMENT_HELPERS:
        _assert_literal_replacement_result_matches_cpython(
            backend_name=backend_name,
            context="compiled-pattern module count coercion",
            helper=helper,
            pattern=pattern,
            replacement=replacement,
            string=string,
            count=count,
            observed=getattr(
                backend,
                helper,
            )(observed_pattern, replacement, string, count=count),
            expected=getattr(
                re,
                helper,
            )(expected_pattern, replacement, string, count=count),
        )


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


def _capture_type_error(callback: Callable[[], object]) -> TypeError:
    with pytest.raises(TypeError) as captured:
        callback()
    return captured.value


def _capture_exception(callback: Callable[[], object]) -> BaseException:
    try:
        callback()
    except BaseException as exc:
        return exc
    raise AssertionError("expected callback to raise")


def _invoke_literal_replacement_helper(
    regex_api: object,
    *,
    helper: str,
    use_compiled_pattern: bool,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> object:
    if use_compiled_pattern:
        compiled = regex_api.compile(pattern)
        return getattr(compiled, helper)(replacement, string)
    return getattr(regex_api, helper)(pattern, replacement, string)


@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
@pytest.mark.parametrize(
    ("use_compiled_pattern", "pattern", "replacement", "string"),
    (
        pytest.param(
            False,
            "abc",
            "x",
            b"abc",
            id="module-str-pattern-on-bytes-string",
        ),
        pytest.param(
            False,
            b"abc",
            b"x",
            "abc",
            id="module-bytes-pattern-on-str-string",
        ),
        pytest.param(
            False,
            "abc",
            b"x",
            "abc",
            id="module-bytes-replacement-on-str-pattern",
        ),
        pytest.param(
            False,
            b"abc",
            "x",
            b"abc",
            id="module-str-replacement-on-bytes-pattern",
        ),
        pytest.param(
            True,
            "abc",
            "x",
            b"abc",
            id="pattern-str-pattern-on-bytes-string",
        ),
        pytest.param(
            True,
            b"abc",
            b"x",
            "abc",
            id="pattern-bytes-pattern-on-str-string",
        ),
        pytest.param(
            True,
            "abc",
            b"x",
            "abc",
            id="pattern-bytes-replacement-on-str-pattern",
        ),
        pytest.param(
            True,
            b"abc",
            "x",
            b"abc",
            id="pattern-str-replacement-on-bytes-pattern",
        ),
    ),
)
def test_source_package_literal_replacement_helpers_match_cpython_type_errors(
    helper: str,
    use_compiled_pattern: bool,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    observed_error = _capture_type_error(
        lambda: _invoke_literal_replacement_helper(
            rebar,
            helper=helper,
            use_compiled_pattern=use_compiled_pattern,
            pattern=pattern,
            replacement=replacement,
            string=string,
        )
    )
    expected_error = _capture_type_error(
        lambda: _invoke_literal_replacement_helper(
            re,
            helper=helper,
            use_compiled_pattern=use_compiled_pattern,
            pattern=pattern,
            replacement=replacement,
            string=string,
        )
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
def test_literal_replacement_count_indexlike_calls___index___once_for_module_helpers(
    regex_backend: tuple[str, object],
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend
    observed_value = _RecordingIndexLike(2)
    expected_value = _RecordingIndexLike(2)

    observed = getattr(backend, helper)(
        pattern,
        replacement,
        string,
        count=observed_value,
    )
    expected = getattr(re, helper)(
        pattern,
        replacement,
        string,
        count=expected_value,
    )

    _assert_literal_replacement_result_matches_cpython(
        backend_name=backend_name,
        context="module count __index__ call count",
        helper=helper,
        pattern=pattern,
        replacement=replacement,
        string=string,
        count=observed_value,
        observed=observed,
        expected=expected,
    )
    assert observed_value.calls == 1
    assert expected_value.calls == 1


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
def test_literal_replacement_count_indexlike_calls___index___once_for_pattern_helpers(
    regex_backend: tuple[str, object],
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )
    observed_value = _RecordingIndexLike(2)
    expected_value = _RecordingIndexLike(2)

    observed = getattr(observed_pattern, helper)(
        replacement,
        string,
        count=observed_value,
    )
    expected = getattr(expected_pattern, helper)(
        replacement,
        string,
        count=expected_value,
    )

    _assert_literal_replacement_result_matches_cpython(
        backend_name=backend_name,
        context="pattern count __index__ call count",
        helper=helper,
        pattern=pattern,
        replacement=replacement,
        string=string,
        count=observed_value,
        observed=observed,
        expected=expected,
    )
    assert observed_value.calls == 1
    assert expected_value.calls == 1


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
def test_literal_replacement_count_indexlike_calls___index___once_for_compiled_pattern_module_helpers(
    regex_backend: tuple[str, object],
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )
    observed_value = _RecordingIndexLike(2)
    expected_value = _RecordingIndexLike(2)

    observed = getattr(backend, helper)(
        observed_pattern,
        replacement,
        string,
        count=observed_value,
    )
    expected = getattr(re, helper)(
        expected_pattern,
        replacement,
        string,
        count=expected_value,
    )

    _assert_literal_replacement_result_matches_cpython(
        backend_name=backend_name,
        context="compiled-pattern module count __index__ call count",
        helper=helper,
        pattern=pattern,
        replacement=replacement,
        string=string,
        count=observed_value,
        observed=observed,
        expected=expected,
    )
    assert observed_value.calls == 1
    assert expected_value.calls == 1


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
def test_literal_replacement_count_indexlike_exceptions_match_cpython_for_module_helpers(
    regex_backend: tuple[str, object],
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    _, backend = regex_backend
    observed_value = _RecordingIndexLike(
        error=_IndexLikeBoomError(f"indexlike boom for module {helper}")
    )
    expected_value = _RecordingIndexLike(
        error=_IndexLikeBoomError(f"indexlike boom for module {helper}")
    )

    observed_error = _capture_exception(
        lambda: getattr(backend, helper)(
            pattern,
            replacement,
            string,
            count=observed_value,
        )
    )
    expected_error = _capture_exception(
        lambda: getattr(re, helper)(
            pattern,
            replacement,
            string,
            count=expected_value,
        )
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args
    assert observed_value.calls == 1
    assert expected_value.calls == 1


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
def test_literal_replacement_count_indexlike_exceptions_match_cpython_for_pattern_helpers(
    regex_backend: tuple[str, object],
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )
    observed_value = _RecordingIndexLike(
        error=_IndexLikeBoomError(f"indexlike boom for pattern {helper}")
    )
    expected_value = _RecordingIndexLike(
        error=_IndexLikeBoomError(f"indexlike boom for pattern {helper}")
    )

    observed_error = _capture_exception(
        lambda: getattr(observed_pattern, helper)(
            replacement,
            string,
            count=observed_value,
        )
    )
    expected_error = _capture_exception(
        lambda: getattr(expected_pattern, helper)(
            replacement,
            string,
            count=expected_value,
        )
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args
    assert observed_value.calls == 1
    assert expected_value.calls == 1


@pytest.mark.parametrize(
    ("pattern", "replacement", "string"),
    _LITERAL_REPLACEMENT_COUNT_COERCION_CASES,
)
@pytest.mark.parametrize("helper", _LITERAL_REPLACEMENT_HELPERS)
def test_literal_replacement_count_indexlike_exceptions_match_cpython_for_compiled_pattern_module_helpers(
    regex_backend: tuple[str, object],
    helper: str,
    pattern: TextValue,
    replacement: TextValue,
    string: TextValue,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )
    observed_value = _RecordingIndexLike(
        error=_IndexLikeBoomError(
            f"indexlike boom for compiled-pattern module {helper}"
        )
    )
    expected_value = _RecordingIndexLike(
        error=_IndexLikeBoomError(
            f"indexlike boom for compiled-pattern module {helper}"
        )
    )

    observed_error = _capture_exception(
        lambda: getattr(backend, helper)(
            observed_pattern,
            replacement,
            string,
            count=observed_value,
        )
    )
    expected_error = _capture_exception(
        lambda: getattr(re, helper)(
            expected_pattern,
            replacement,
            string,
            count=expected_value,
        )
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args
    assert observed_value.calls == 1
    assert expected_value.calls == 1


def test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation(
) -> None:
    with pytest.raises(NotImplementedError) as module_template:
        rebar.sub("abc", r"\1", "abc")

    assert_placeholder_message_contains(
        module_template.value,
        "rebar.sub() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}

    with pytest.raises(NotImplementedError) as module_flags:
        rebar.subn("abc", "x", "abc", flags=rebar.IGNORECASE)

    assert_placeholder_message_contains(
        module_flags.value,
        "rebar.subn() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}

    with pytest.raises(NotImplementedError) as module_meta:
        rebar.sub("[ab]c", "x", "abc")

    assert_placeholder_message_contains(
        module_meta.value,
        "rebar.compile() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}

    with pytest.raises(NotImplementedError) as module_empty:
        rebar.sub("", "x", "abc")

    assert_placeholder_message_contains(
        module_empty.value,
        "rebar.sub() is a scaffold placeholder",
    )
    assert rebar._COMPILE_CACHE == {}


def test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases(
) -> None:
    flagged_pattern = rebar.compile("abc", rebar.IGNORECASE)
    with pytest.raises(NotImplementedError) as bound_flags:
        flagged_pattern.sub("x", "abc")

    assert_placeholder_message_contains(
        bound_flags.value,
        "rebar.Pattern.sub() is a scaffold placeholder",
    )

    empty_pattern = rebar.compile("")
    with pytest.raises(NotImplementedError) as bound_empty:
        empty_pattern.subn("x", "abc")

    assert_placeholder_message_contains(
        bound_empty.value,
        "rebar.Pattern.subn() is a scaffold placeholder",
    )

    with pytest.raises(NotImplementedError) as bound_template:
        rebar.compile("abc").sub(r"\1", "abc")

    assert_placeholder_message_contains(
        bound_template.value,
        "rebar.Pattern.sub() is a scaffold placeholder",
    )
