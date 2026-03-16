from __future__ import annotations

import pathlib
from collections.abc import Iterable
from functools import cache
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

from rebar_harness.benchmarks import (
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    determine_phase,
    determine_runner_version,
    load_manifest,
    load_manifests,
    select_benchmark_manifest_path,
    select_benchmark_manifest_paths,
    select_workloads,
    workload_to_payload,
)
from tests.harness_cli_test_support import run_harness_scorecard


BASE_SOURCE_TREE_MANIFEST_IDS = frozenset({"compile-matrix", "regression-matrix"})


def _full_source_tree_scorecard_case_definition(
    *,
    manifest_ids: tuple[str, ...],
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    expected_first_deferred: dict[str, str] | None = None,
    workload_note_substrings: dict[str, str] | None = None,
) -> dict[str, Any]:
    case_definition: dict[str, Any] = {"full_manifest_ids": manifest_ids}
    if representative_measured_workload_ids is not None:
        case_definition["representative_measured_workload_ids"] = (
            representative_measured_workload_ids
        )
    if representative_known_gap_workload_ids is not None:
        case_definition["representative_known_gap_workload_ids"] = (
            representative_known_gap_workload_ids
        )
    if expected_first_deferred is not None:
        case_definition["expected_first_deferred"] = expected_first_deferred
    if workload_note_substrings is not None:
        case_definition["workload_note_substrings"] = workload_note_substrings
    return case_definition


def _derived_source_tree_scorecard_case_definition(
    *,
    manifest_ids: tuple[str, ...],
    selection_mode: str,
    manifest_known_gap_counts: dict[str, int] | None = None,
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    expected_first_deferred: dict[str, str] | None = None,
    expected_workload_order: tuple[str, ...] | None = None,
    workload_note_substrings: dict[str, str] | None = None,
) -> dict[str, Any]:
    case_definition: dict[str, Any] = {
        "manifest_ids": manifest_ids,
        "selection_mode": selection_mode,
    }
    if manifest_known_gap_counts is not None:
        case_definition["_derived_manifest_known_gap_counts"] = manifest_known_gap_counts
    if representative_measured_workload_ids is not None:
        case_definition["representative_measured_workload_ids"] = (
            representative_measured_workload_ids
        )
    if representative_known_gap_workload_ids is not None:
        case_definition["representative_known_gap_workload_ids"] = (
            representative_known_gap_workload_ids
        )
    if expected_first_deferred is not None:
        case_definition["expected_first_deferred"] = expected_first_deferred
    if expected_workload_order is not None:
        case_definition["expected_workload_order"] = expected_workload_order
    if workload_note_substrings is not None:
        case_definition["workload_note_substrings"] = workload_note_substrings
    return case_definition


SOURCE_TREE_SCORECARD_EXPECTATIONS: dict[str, dict[str, Any]] = {
    "compile-smoke": _derived_source_tree_scorecard_case_definition(
        manifest_ids=("compile-smoke",),
        selection_mode="full",
        manifest_known_gap_counts={"compile-smoke": 1},
        expected_first_deferred={
            "area": "module-boundary",
            "follow_up": "RBR-0015",
        },
        representative_measured_workload_ids=("compile-literal-cold",),
        representative_known_gap_workload_ids=("compile-character-class-warm",),
    ),
    "compile-matrix": _full_source_tree_scorecard_case_definition(
        manifest_ids=("compile-matrix",),
        expected_first_deferred={
            "area": "module-boundary",
            "follow_up": "RBR-0015",
        },
        representative_measured_workload_ids=(
            "compile-inline-locale-bytes-warm",
            "compile-lookbehind-cold",
            "compile-atomic-group-purged",
            "compile-parser-stress-cold",
        ),
    ),
    "post-parser-workflows": _full_source_tree_scorecard_case_definition(
        manifest_ids=(
            "module-boundary",
            "collection-replacement-boundary",
            "literal-flag-boundary",
        ),
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "module-search-grouped-literal-cold-hit",
            "module-findall-single-dot-warm-str",
            "module-sub-template-warm-str",
            "pattern-subn-grouped-template-warm-str",
            "module-search-inline-flag-warm-str-hit",
            "pattern-search-inline-flag-warm-str-hit",
            "module-search-locale-purged-bytes-hit",
            "pattern-search-locale-purged-bytes-hit",
        ),
        representative_known_gap_workload_ids=(
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ),
    ),
    "nested-group-replacement-boundary": _full_source_tree_scorecard_case_definition(
        manifest_ids=("nested-group-replacement-boundary",),
    ),
    "nested-group-callable-replacement-boundary": _full_source_tree_scorecard_case_definition(
        manifest_ids=("nested-group-callable-replacement-boundary",),
    ),
    "branch-local-backreference-boundary": _full_source_tree_scorecard_case_definition(
        manifest_ids=("branch-local-backreference-boundary",),
    ),
    "conditional-group-exists-boundary": _full_source_tree_scorecard_case_definition(
        manifest_ids=("conditional-group-exists-boundary",),
    ),
    "regression-pack-full": _full_source_tree_scorecard_case_definition(
        manifest_ids=(
            "compile-matrix",
            "module-boundary",
            "regression-matrix",
        ),
        representative_measured_workload_ids=(
            "compile-inline-locale-bytes-warm",
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "regression-import-cold",
            "regression-module-search-bytes-cold-miss",
        ),
        representative_known_gap_workload_ids=(
            "regression-parser-bytes-backreference-purged",
        ),
    ),
    "regression-pack-smoke": _derived_source_tree_scorecard_case_definition(
        manifest_ids=("regression-matrix",),
        selection_mode="smoke",
        expected_workload_order=(
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        representative_measured_workload_ids=(
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        representative_known_gap_workload_ids=(),
    ),
}

SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = {
    "compile-matrix": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "module-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "import-module-cold",
            "module-search-grouped-literal-cold-hit",
            "module-search-literal-warm-hit",
            "module-search-bytes-cold-miss",
        ),
    },
    "pattern-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "pattern-search-literal-warm-hit",
            "pattern-fullmatch-bytes-purged-hit",
        ),
    },
    "collection-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "literal-flag-boundary": {
        "known_gap_workload_ids": (
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-ignorecase-ascii-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-named-boundary": {
        "known_gap_workload_ids": (
            "module-search-grouped-segment-cold-gap",
            "pattern-search-grouped-segment-warm-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-grouped-segment-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "numbered-backreference-boundary": {
        "known_gap_workload_ids": (
            "module-search-numbered-backreference-segment-cold-gap",
            "pattern-search-numbered-backreference-prefix-purged-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-numbered-backreference-segment-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-segment-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "literal-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "grouped-alternation-boundary": {
        "known_gap_workload_ids": (
            "module-sub-template-nested-grouped-alternation-warm-gap",
            "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-sub-template-nested-grouped-alternation-warm-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-alternation-replacement-boundary": {
        "known_gap_workload_ids": (
            "module-sub-template-nested-grouped-alternation-cold-gap",
            "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-sub-template-nested-grouped-alternation-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "grouped-alternation-callable-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "nested-group-boundary": {
        "known_gap_workload_ids": (
            "module-search-triple-nested-group-cold-gap",
            "pattern-fullmatch-named-quantified-nested-group-purged-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-triple-nested-group-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "nested-group-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "nested-group-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "nested-group-callable-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "branch-local-backreference-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "optional-group-boundary": {
        "known_gap_workload_ids": (
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "exact-repeat-quantified-group-boundary": {
        "known_gap_workload_ids": (
            "module-search-numbered-broader-ranged-repeat-group-cold-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-numbered-broader-ranged-repeat-group-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "ranged-repeat-quantified-group-boundary": {
        "known_gap_workload_ids": (
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        ),
        "representative_known_gap_workload_ids": (
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        ),
        "representative_measured_workload_ids": (),
    },
    "wider-ranged-repeat-quantified-group-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-str",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-str",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-str",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
        ),
        "shape_expectation": {
            "representative_measured_workload_ids": (
                "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
            ),
            "pattern_groups": (
                {
                    "slice_id": "nested-broader-range-grouped-alternation",
                    "patterns": (
                        "a((bc|de){1,4})d",
                        "a(?P<outer>(bc|de){1,4})d",
                    ),
                    "minimum_rows": 6,
                    "required_operations": (
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    "required_categories": (
                        "nested-group",
                        "alternation",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    "search_haystacks": (),
                    "search_haystack_substrings": (
                        "abcd",
                        "aded",
                    ),
                    "pattern_haystacks": (
                        "abcbcded",
                        "adedededed",
                    ),
                },
                {
                    "slice_id": "nested-broader-range-grouped-conditional",
                    "patterns": (
                        "a(((bc|de){1,4})d)?(?(1)e|f)",
                        "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
                    ),
                    "minimum_rows": 7,
                    "required_operations": (
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    "required_categories": (
                        "nested-group",
                        "alternation",
                        "conditional",
                        "optional-group",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    "search_haystacks": (
                        "zzafzz",
                        "zzabcdezz",
                        "zzadedezz",
                    ),
                    "search_haystack_substrings": (),
                    "pattern_haystacks": (
                        "abcbcdede",
                        "adedededede",
                    ),
                },
                {
                    "slice_id": "nested-broader-range-grouped-backtracking-heavy",
                    "patterns": (
                        "a(((bc|b)c){1,4})d",
                        "a(?P<outer>((bc|b)c){1,4})d",
                    ),
                    "minimum_rows": 7,
                    "required_operations": (
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    "required_categories": (
                        "grouped",
                        "nested-group",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    "search_haystacks": (
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    "search_haystack_substrings": (),
                    "pattern_haystacks": (
                        "abcbccd",
                        "abccbcd",
                        "abcbccbccbcd",
                    ),
                },
            ),
        },
    },
    "open-ended-quantified-group-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
        ),
    },
    "quantified-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "optional-group-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-no-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-empty-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-empty-yes-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "conditional-group-exists-fully-empty-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_ids": (),
        "representative_measured_workload_ids": (),
    },
    "regression-matrix": {
        "known_gap_count": 1,
        "known_gap_workload_ids": (
            "regression-parser-bytes-backreference-purged",
        ),
        "representative_known_gap_workload_ids": (
            "regression-parser-bytes-backreference-purged",
        ),
        "representative_measured_workload_ids": (),
    },
}


def _combined_slice_expectation(
    *,
    manifest_id: str,
    slice_id: str,
    required_syntax_features: tuple[str, ...] = (),
    excluded_syntax_features: tuple[str, ...] = (),
    required_categories: tuple[str, ...] = (),
    excluded_categories: tuple[str, ...] = (),
    required_id_suffix: str | None = None,
    expected_workload_ids: tuple[str, ...],
    expected_patterns: set[str],
    expected_operations: set[str],
    expected_haystacks: set[str],
    required_row_categories: tuple[str, ...],
    expected_status: str = "measured",
) -> dict[str, Any]:
    return {
        "expected_haystacks": expected_haystacks,
        "expected_operations": expected_operations,
        "expected_patterns": expected_patterns,
        "expected_status": expected_status,
        "expected_workload_ids": expected_workload_ids,
        "excluded_categories": excluded_categories,
        "excluded_syntax_features": excluded_syntax_features,
        "manifest_id": manifest_id,
        "required_categories": required_categories,
        "required_id_suffix": required_id_suffix,
        "required_row_categories": required_row_categories,
        "required_syntax_features": required_syntax_features,
        "slice_id": slice_id,
    }


SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS = (
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="anchored-module-compile-cluster",
        required_syntax_features=("module-compile", "literal-text"),
        required_categories=("compile", "literal"),
        expected_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
        ),
        expected_patterns={r"^abc$"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="branch-local-backreference-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "nested-groups",
            "counted-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbbdzz", "abcbccd", "zzacccdzz", "abbbd"},
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "branch-local",
            "conditional",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-search-nested-group-quantified-alternation-cold-gap",
            "pattern-fullmatch-numbered-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "module-search-named-quantified-nested-group-alternation-lower-bound-c-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
        ),
        expected_patterns={
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        },
        expected_operations={"module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabdzz", "acbbd", "zzacdzz", "abccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="non-quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences",),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
            "module-compile-named-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
        ),
        expected_patterns={
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "accd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "quantifiers"),
        excluded_syntax_features=("counted-repeats",),
        expected_workload_ids=(
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str",
        ),
        expected_patterns={
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "abccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "counted-repeats",
            "ranged-repeats",
        ),
        expected_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "acccccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "counted-repeats"),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbbdzz", "acccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-alternation",
        required_syntax_features=("alternation", "callable-replacement"),
        excluded_syntax_features=("branch-local-backreferences", "quantifiers"),
        expected_workload_ids=(
            "module-sub-callable-nested-group-alternation-cold-gap",
            "pattern-subn-callable-numbered-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-named-nested-group-alternation-c-branch-warm-str",
            "pattern-subn-callable-named-nested-group-alternation-b-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c))d",
            r"a(?P<outer>(?P<inner>b|c))d",
        },
        expected_operations={"module.sub", "pattern.subn"},
        expected_haystacks={"abdacd", "acdabd", "acd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=("callable-replacement", "quantifiers"),
        excluded_syntax_features=("alternation", "branch-local-backreferences"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
        ),
        expected_patterns={
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "callable-replacement", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabdzz", "zzabccdacbbdzz", "zzabccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-str",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-str",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbdaccd", "accd", "accdabbd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("counted-repeats", "ranged-repeats"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzabccdzz", "zzaccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abcbccdabbd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=("quantifiers", "replacement-template"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
            "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
            "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
        ),
        expected_patterns={
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "template",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="grouped-alternation-callable-replacement-boundary",
        slice_id="former-gap-callable-replacement-rows",
        required_syntax_features=("callable-replacement",),
        required_id_suffix="gap",
        expected_workload_ids=(
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
        expected_patterns={
            r"a((b|c))d",
            r"a(?P<outer>(b|c))d",
        },
        expected_operations={"module.sub", "pattern.subn"},
        expected_haystacks={"abdacd", "acdabd"},
        required_row_categories=(
            "alternation",
            "replacement",
            "callable",
            "gap",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-template-replacement-rows",
        required_syntax_features=("conditionals", "replacement-template"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation-heavy",
            "nested-group",
            "quantified",
            "unsupported",
            "callable",
        ),
        expected_workload_ids=(
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-str",
            "module-sub-template-named-conditional-group-exists-replacement-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzacezz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "template",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "exception",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-str",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcdacezz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("exception",),
        excluded_categories=("alternation", "nested-group", "quantified", "unsupported"),
        expected_workload_ids=(
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.subn", "pattern.subn"},
        expected_haystacks={"zzacezz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "absent",
            "count",
            "exception",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-alternation-heavy-constant-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "quantifiers"),
        required_categories=("alternation-heavy", "replacement", "quantified"),
        expected_workload_ids=(
            "module-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "module-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "zzabcdedezz",
            "zzabcdfdfzz",
            "zzacegegzz",
            "zzacehehzz",
        },
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "quantified",
            "replacement",
        ),
    ),
)


def _compile_smoke_manifest_path() -> pathlib.Path:
    return select_benchmark_manifest_path(COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR)


def _published_full_suite_manifest_paths() -> tuple[pathlib.Path, ...]:
    return select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)


@cache
def _source_tree_manifest_records() -> dict[str, tuple[pathlib.Path, dict[str, Any]]]:
    records: dict[str, tuple[pathlib.Path, dict[str, Any]]] = {}
    for path in (_compile_smoke_manifest_path(), *_published_full_suite_manifest_paths()):
        raw_manifest, _ = load_manifest(path)
        manifest_id = str(raw_manifest["manifest_id"])
        if manifest_id in records:
            raise AssertionError(f"duplicate benchmark manifest id {manifest_id!r}")
        records[manifest_id] = (path, raw_manifest)
    return records


def manifest_id_for_path(path: pathlib.Path) -> str:
    resolved_path = path.resolve()
    for manifest_id, (manifest_path, _) in _source_tree_manifest_records().items():
        if manifest_path.resolve() == resolved_path:
            return manifest_id
    raise AssertionError(f"unknown benchmark manifest path {path}")


def manifest_path_for_id(manifest_id: str) -> pathlib.Path:
    try:
        return _source_tree_manifest_records()[manifest_id][0]
    except KeyError as exc:
        raise AssertionError(f"unknown benchmark manifest id {manifest_id!r}") from exc


def relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run_source_tree_benchmark_scorecard(
    manifest_paths: Iterable[pathlib.Path],
    *,
    smoke: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = []
    for manifest_path in manifest_paths:
        command.extend(("--manifest", str(manifest_path)))
    if smoke:
        command.append("--smoke")

    return run_harness_scorecard(
        "rebar_harness.benchmarks",
        command,
        report_name="benchmarks.json",
    )


def ordered_operations(workloads: list[dict[str, Any]]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = str(workload["operation"])
        if operation not in operations:
            operations.append(operation)
    return operations


def source_tree_scorecard_case_ids() -> tuple[str, ...]:
    return tuple(SOURCE_TREE_SCORECARD_EXPECTATIONS)


def _append_unique_workload_ids(
    representative_ids: list[str],
    workload_ids: Iterable[str],
) -> None:
    for workload_id in workload_ids:
        normalized_workload_id = str(workload_id)
        if normalized_workload_id not in representative_ids:
            representative_ids.append(normalized_workload_id)


def source_tree_combined_manifest_representative_measured_workload_ids(
    manifest_id: str,
) -> tuple[str, ...]:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )

    explicit_workload_ids = tuple(
        str(workload_id)
        for workload_id in manifest_expectation["representative_measured_workload_ids"]
    )
    if explicit_workload_ids:
        return explicit_workload_ids

    representative_ids: list[str] = []
    shape_expectation = manifest_expectation.get("shape_expectation")
    if shape_expectation is not None:
        _append_unique_workload_ids(
            representative_ids,
            shape_expectation.get("representative_measured_workload_ids", ()),
        )
    for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS:
        if expectation["manifest_id"] != manifest_id:
            continue
        _append_unique_workload_ids(
            representative_ids,
            expectation["expected_workload_ids"],
        )
    return tuple(representative_ids)


def _source_tree_manifest_known_gap_count(
    manifest_expectation: dict[str, Any],
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> int:
    known_gap_workload_ids = tuple(
        str(workload_id)
        for workload_id in manifest_expectation.get("known_gap_workload_ids", ())
    )
    if known_gap_workload_ids:
        if selected_workload_ids is None:
            return len(known_gap_workload_ids)
        selected_workload_id_set = {
            str(workload_id) for workload_id in selected_workload_ids
        }
        return sum(
            1
            for workload_id in known_gap_workload_ids
            if workload_id in selected_workload_id_set
        )
    return int(manifest_expectation.get("known_gap_count", 0))


def _public_source_tree_manifest_expectation(
    manifest_id: str,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    return {
        **manifest_expectation,
        "known_gap_count": _source_tree_manifest_known_gap_count(
            manifest_expectation,
            selected_workload_ids=selected_workload_ids,
        ),
    }


def _source_tree_manifest_known_gap_counts(
    manifest_ids: tuple[str, ...],
    case_definition: dict[str, Any],
    *,
    selected_workload_ids_by_manifest: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, int]:
    explicit_known_gap_counts = case_definition.get("_derived_manifest_known_gap_counts", {})
    known_gap_counts: dict[str, int] = {}
    for manifest_id in manifest_ids:
        if manifest_id in explicit_known_gap_counts:
            known_gap_counts[manifest_id] = int(explicit_known_gap_counts[manifest_id])
            continue
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
        if manifest_expectation is None:
            raise AssertionError(
                "missing known-gap expectation for source-tree scorecard manifest "
                f"{manifest_id!r}"
            )
        known_gap_counts[manifest_id] = _source_tree_manifest_known_gap_count(
            manifest_expectation,
            selected_workload_ids=(
                selected_workload_ids_by_manifest.get(manifest_id, ())
                if selected_workload_ids_by_manifest is not None
                else None
            ),
        )
    return known_gap_counts


def _resolve_source_tree_scorecard_case_definition(
    case_definition: dict[str, Any],
) -> dict[str, Any]:
    full_manifest_ids = case_definition.get("full_manifest_ids")
    if full_manifest_ids is None:
        return case_definition

    manifest_records = _source_tree_manifest_records()
    manifest_documents: list[dict[str, Any]] = []
    manifest_expectations: dict[str, dict[str, int]] = {}
    for manifest_id in full_manifest_ids:
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
        if manifest_expectation is None:
            raise AssertionError(
                "unknown full source-tree scorecard expectation "
                f"{manifest_id!r}"
            )
        manifest_documents.append(manifest_records[manifest_id][1])
        manifest_expectations[manifest_id] = {
            "known_gap_count": _source_tree_manifest_known_gap_count(
                manifest_expectation
            ),
        }

    resolved_case_definition = {
        key: value
        for key, value in case_definition.items()
        if key != "full_manifest_ids"
    }
    resolved_case_definition["manifest_ids"] = full_manifest_ids
    resolved_case_definition["selection_mode"] = "full"
    resolved_case_definition["expected_summary"] = expected_summary_for_manifests(
        manifest_documents
    )
    resolved_case_definition["manifest_expectations"] = manifest_expectations
    if len(full_manifest_ids) == 1:
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[full_manifest_ids[0]]
        resolved_case_definition.setdefault(
            "representative_measured_workload_ids",
            source_tree_combined_manifest_representative_measured_workload_ids(
                full_manifest_ids[0]
            ),
        )
        resolved_case_definition.setdefault(
            "representative_known_gap_workload_ids",
            manifest_expectation["representative_known_gap_workload_ids"],
        )
    return resolved_case_definition


def source_tree_scorecard_case(case_id: str) -> dict[str, Any]:
    if case_id not in SOURCE_TREE_SCORECARD_EXPECTATIONS:
        raise AssertionError(f"unknown source-tree scorecard case {case_id!r}")

    case_definition = _resolve_source_tree_scorecard_case_definition(
        SOURCE_TREE_SCORECARD_EXPECTATIONS[case_id]
    )
    manifest_ids = tuple(case_definition["manifest_ids"])
    manifest_paths = [manifest_path_for_id(manifest_id) for manifest_id in manifest_ids]
    raw_manifests, manifest_workloads = load_manifests(manifest_paths)
    selected_workloads = select_workloads(
        manifest_workloads,
        smoke_only=case_definition["selection_mode"] == "smoke",
    )
    selected_workload_ids_by_manifest = {
        manifest_id: tuple(
            workload.workload_id
            for workload in selected_workloads
            if workload.manifest_id == manifest_id
        )
        for manifest_id in manifest_ids
    }
    workload_payloads = [
        workload_to_payload(workload)
        for workload in selected_workloads
    ]
    manifest_known_gap_counts = _source_tree_manifest_known_gap_counts(
        manifest_ids,
        case_definition,
        selected_workload_ids_by_manifest=selected_workload_ids_by_manifest,
    )
    public_case_definition = {
        key: value
        for key, value in case_definition.items()
        if key != "_derived_manifest_known_gap_counts"
    }
    public_case_definition.setdefault(
        "expected_summary",
        expected_summary_for_manifests(
            raw_manifests,
            selected_workload_ids_by_manifest=selected_workload_ids_by_manifest,
            manifest_known_gap_counts=manifest_known_gap_counts,
        ),
    )
    public_case_definition.setdefault(
        "manifest_expectations",
        {
            manifest_id: {"known_gap_count": manifest_known_gap_counts[manifest_id]}
            for manifest_id in manifest_ids
        },
    )

    return {
        **public_case_definition,
        "case_id": case_id,
        "expected_adapter": (
            "rebar.module-surface"
            if any(workload.family == "module" for workload in selected_workloads)
            else "rebar.compile"
        ),
        "expected_manifest_paths": [
            relative_manifest_path(path) for path in manifest_paths
        ],
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "manifest_documents": raw_manifests,
        "manifest_documents_by_id": {
            str(raw_manifest["manifest_id"]): raw_manifest for raw_manifest in raw_manifests
        },
        "manifest_paths": manifest_paths,
        "manifest_paths_by_id": {
            manifest_id: relative_manifest_path(manifest_path_for_id(manifest_id))
            for manifest_id in manifest_ids
        },
        "selected_workload_ids_by_manifest": selected_workload_ids_by_manifest,
    }


def source_tree_combined_target_manifest_ids() -> tuple[str, ...]:
    target_manifest_ids = tuple(
        manifest_id
        for path in _published_full_suite_manifest_paths()
        if (manifest_id := manifest_id_for_path(path)) not in BASE_SOURCE_TREE_MANIFEST_IDS
    )
    target_ids = set(target_manifest_ids)
    missing_expectations = target_ids - set(SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS)
    if missing_expectations:
        raise AssertionError(
            "source-tree combined manifest expectations drifted from the published full-suite selector: "
            f"missing {sorted(missing_expectations)}"
        )
    return target_manifest_ids


def selected_manifest_paths_for_target_manifest(target_manifest_id: str) -> list[pathlib.Path]:
    manifest_paths: list[pathlib.Path] = []
    published_manifest_paths = _published_full_suite_manifest_paths()
    regression_path = next(
        (
            path
            for path in published_manifest_paths
            if manifest_id_for_path(path) == "regression-matrix"
        ),
        None,
    )
    for path in published_manifest_paths:
        manifest_id = manifest_id_for_path(path)
        if manifest_id == "regression-matrix":
            continue
        manifest_paths.append(path)
        if manifest_id == target_manifest_id:
            break
    else:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in the published full-suite selector"
        )
    if target_manifest_id != "module-boundary":
        if regression_path is None:
            raise AssertionError(
                "the published full-suite selector is missing the regression-matrix manifest"
            )
        manifest_paths.append(regression_path)
    return manifest_paths


def expected_summary_for_manifests(
    manifest_documents: list[dict[str, Any]],
    *,
    selected_workload_ids_by_manifest: dict[str, tuple[str, ...]] | None = None,
    manifest_known_gap_counts: dict[str, int] | None = None,
) -> dict[str, int]:
    selected_workload_ids = (
        {
            manifest_id: set(workload_ids)
            for manifest_id, workload_ids in selected_workload_ids_by_manifest.items()
        }
        if selected_workload_ids_by_manifest is not None
        else None
    )
    workloads: list[dict[str, Any]] = []
    regression_workloads = 0
    selected_manifest_ids: list[str] = []
    for manifest in manifest_documents:
        manifest_id = str(manifest["manifest_id"])
        manifest_workloads = manifest["workloads"]
        if selected_workload_ids is None:
            selected_manifest_workloads = manifest_workloads
        else:
            selected_manifest_workloads = [
                workload
                for workload in manifest_workloads
                if str(workload["id"]) in selected_workload_ids.get(manifest_id, set())
            ]
        if selected_manifest_workloads:
            selected_manifest_ids.append(manifest_id)
        if manifest_id == "regression-matrix":
            regression_workloads += len(selected_manifest_workloads)
        workloads.extend(selected_manifest_workloads)
    known_gap_counts = (
        manifest_known_gap_counts
        if manifest_known_gap_counts is not None
        else {
            str(manifest["manifest_id"]): _source_tree_manifest_known_gap_count(
                SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[str(manifest["manifest_id"])]
            )
            for manifest in manifest_documents
            if str(manifest["manifest_id"]) in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
        }
    )
    known_gap_count = sum(
        known_gap_counts.get(manifest_id, 0) for manifest_id in selected_manifest_ids
    )
    return {
        "known_gap_count": known_gap_count,
        "measured_workloads": len(workloads) - known_gap_count,
        "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
        "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
        "regression_workloads": regression_workloads,
        "total_workloads": len(workloads),
    }


def representative_measured_workload_ids(
    scorecard: dict[str, Any],
    manifest_document: dict[str, Any],
    *,
    extra_workload_ids: tuple[str, ...] = (),
) -> list[str]:
    manifest_id = str(manifest_document["manifest_id"])
    representative_ids: list[str] = []
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is not None:
        _append_unique_workload_ids(
            representative_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
    _append_unique_workload_ids(representative_ids, extra_workload_ids)
    for operation in ordered_operations(manifest_document["workloads"]):
        for workload in scorecard["workloads"]:
            if workload["manifest_id"] != manifest_id:
                continue
            if workload["operation"] != operation or workload["status"] != "measured":
                continue
            workload_id = str(workload["id"])
            if workload_id not in representative_ids:
                representative_ids.append(workload_id)
            break
    return representative_ids


def source_tree_combined_case(target_manifest_id: str) -> dict[str, Any]:
    manifest_paths = selected_manifest_paths_for_target_manifest(target_manifest_id)
    raw_manifests, workloads = load_manifests(list(manifest_paths))
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    target_manifest = next(
        manifest for manifest in raw_manifests if manifest["manifest_id"] == target_manifest_id
    )
    return {
        "expected_adapter": (
            "rebar.module-surface"
            if any(workload.family == "module" for workload in workloads)
            else "rebar.compile"
        ),
        "expected_manifest_paths": [relative_manifest_path(path) for path in manifest_paths],
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "expected_summary": expected_summary_for_manifests(raw_manifests),
        "manifest_documents": raw_manifests,
        "manifest_documents_by_id": {
            str(raw_manifest["manifest_id"]): raw_manifest for raw_manifest in raw_manifests
        },
        "manifest_expectation": _public_source_tree_manifest_expectation(
            target_manifest_id
        ),
        "manifest_id": target_manifest_id,
        "manifest_path": relative_manifest_path(manifest_path_for_id(target_manifest_id)),
        "manifest_paths": manifest_paths,
        "manifest_paths_by_id": {
            str(raw_manifest["manifest_id"]): relative_manifest_path(path)
            for path, raw_manifest in zip(manifest_paths, raw_manifests, strict=True)
        },
        "selected_workload_ids_by_manifest": {
            str(raw_manifest["manifest_id"]): tuple(
                workload.workload_id
                for workload in workloads
                if workload.manifest_id == str(raw_manifest["manifest_id"])
            )
            for raw_manifest in raw_manifests
        },
        "selection_mode": "full",
        "target_manifest": target_manifest,
    }


def source_tree_combined_manifest_shape_expectation(manifest_id: str) -> dict[str, Any]:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    shape_expectation = manifest_expectation.get("shape_expectation")
    if shape_expectation is None:
        raise AssertionError(
            "source-tree combined manifest "
            f"{manifest_id!r} does not define shared shape expectations"
        )
    return shape_expectation


def source_tree_combined_slice_manifest_ids() -> tuple[str, ...]:
    manifest_ids_with_expectations = {
        expectation["manifest_id"] for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    }
    combined_target_ids = source_tree_combined_target_manifest_ids()
    missing_manifest_ids = manifest_ids_with_expectations - set(combined_target_ids)
    if missing_manifest_ids:
        raise AssertionError(
            "source-tree combined slice expectations reference manifest ids outside the "
            f"published combined selector: {sorted(missing_manifest_ids)}"
        )
    return tuple(
        manifest_id
        for manifest_id in combined_target_ids
        if manifest_id in manifest_ids_with_expectations
    )


def source_tree_combined_slice_expectations(
    manifest_id: str,
) -> tuple[dict[str, Any], ...]:
    expectations = tuple(
        expectation
        for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
        if expectation["manifest_id"] == manifest_id
    )
    if not expectations:
        raise AssertionError(
            f"unknown source-tree combined slice expectation manifest {manifest_id!r}"
        )
    return expectations


def _workload_matches_source_tree_combined_slice(
    workload: dict[str, Any],
    expectation: dict[str, Any],
) -> bool:
    workload_id = str(workload["id"])
    required_id_suffix = expectation["required_id_suffix"]
    if required_id_suffix is not None and not workload_id.endswith(required_id_suffix):
        return False

    syntax_features = set(str(value) for value in workload["syntax_features"])
    categories = set(str(value) for value in workload["categories"])
    return (
        set(expectation["required_syntax_features"]).issubset(syntax_features)
        and syntax_features.isdisjoint(expectation["excluded_syntax_features"])
        and set(expectation["required_categories"]).issubset(categories)
        and categories.isdisjoint(expectation["excluded_categories"])
    )


def select_source_tree_combined_slice_rows(
    manifest_document: dict[str, Any],
    expectation: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        workload
        for workload in manifest_document["workloads"]
        if _workload_matches_source_tree_combined_slice(workload, expectation)
    ]
