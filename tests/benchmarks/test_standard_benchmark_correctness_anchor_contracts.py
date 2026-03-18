from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache
import pathlib
import re
from types import SimpleNamespace
from typing import Any

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)

from tests.benchmarks import correctness_anchor_support as support
from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    assert_anchored_workload_case_result_parity,
    assert_benchmark_workload_matches_expected_result,
    expected_anchored_workload_case_pairs,
    freeze_signature_value,
    published_case_ids_by_signature,
    unanchored_workload_ids,
)
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
)


@pytest.fixture
def anchor_support_cache_guard() -> None:
    _clear_anchor_support_caches()
    yield
    _clear_anchor_support_caches()


def _clear_anchor_support_caches() -> None:
    for cached_function in (
        support._manifest_workloads,
        support.published_case_ids_by_signature,
        support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


def _synthetic_case(
    case_id: str,
    signature: tuple[object, ...] | None,
) -> SimpleNamespace:
    return SimpleNamespace(case_id=case_id, signature=signature)


def _synthetic_workload(
    workload_id: str,
    signature: tuple[object, ...],
    *,
    include: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(workload_id=workload_id, signature=signature, include=include)


@dataclass(frozen=True, slots=True)
class StandardBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    expected_legacy_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )
    callback_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()
    direct_parity_supplemental_cases: tuple[Any, ...] = ()
    run_special_unanchored_result_parity: bool = False


EXPECTED_COMPILE_ANCHOR_CASE_IDS = {
    ("compile_matrix.py", "compile-inline-locale-bytes-warm"): (
        "bytes-inline-locale-flag-success",
    ),
    ("compile_matrix.py", "compile-lookbehind-cold"): (
        "str-fixed-width-lookbehind-success",
    ),
    ("compile_matrix.py", "compile-character-class-ignorecase-warm"): (
        "str-character-class-ignorecase-success",
    ),
    ("compile_matrix.py", "compile-possessive-quantifier-cold"): (
        "str-possessive-quantifier-success",
    ),
    ("compile_matrix.py", "compile-atomic-group-purged"): (
        "str-atomic-group-success",
    ),
    ("compile_matrix.py", "compile-parser-stress-cold"): (
        "str-parser-stress-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-parser-atomic-lookbehind-cold"): (
        "str-parser-stress-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-parser-bytes-backreference-purged"): (
        "bytes-named-backreference-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-module-compile-verbose-purged"): (
        "workflow-compile-str-verbose-regression",
    ),
}

OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)
EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS = {
    (
        "optional_group_boundary.py",
        OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    ): ("optional-group-conditional-module-search-present-str",),
}

EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS = frozenset(
    {
        "module-search-triple-nested-group-cold-gap",
        "pattern-fullmatch-named-quantified-nested-group-purged-gap",
    }
)
EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS = {
    ("nested_group_boundary.py", "module-compile-nested-group-cold-str"): (
        "nested-group-compile-metadata-str",
    ),
    ("nested_group_boundary.py", "module-search-nested-group-warm-str"): (
        "nested-group-module-search-str",
    ),
    ("nested_group_boundary.py", "pattern-fullmatch-nested-group-purged-str"): (
        "nested-group-pattern-fullmatch-str",
    ),
    ("nested_group_boundary.py", "module-compile-named-nested-group-warm-str"): (
        "named-nested-group-compile-metadata-str",
    ),
    ("nested_group_boundary.py", "module-search-named-nested-group-warm-str"): (
        "named-nested-group-module-search-str",
    ),
    ("nested_group_boundary.py", "pattern-fullmatch-named-nested-group-purged-str"): (
        "named-nested-group-pattern-fullmatch-str",
    ),
}

EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS = {
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-compile-numbered-exact-repeat-group-cold-str",
    ): ("exact-repeat-numbered-group-compile-metadata-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-numbered-exact-repeat-group-warm-str",
    ): ("exact-repeat-numbered-group-module-search-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-exact-repeat-group-purged-str",
    ): ("exact-repeat-numbered-group-pattern-fullmatch-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-compile-named-exact-repeat-group-warm-str",
    ): ("exact-repeat-named-group-compile-metadata-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-named-exact-repeat-group-warm-str",
    ): ("exact-repeat-named-group-module-search-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-named-exact-repeat-group-purged-str",
    ): ("exact-repeat-named-group-pattern-fullmatch-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-numbered-broader-ranged-repeat-group-cold-gap",
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS = {
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-compile-numbered-ranged-repeat-group-cold-str",
    ): ("ranged-repeat-numbered-group-compile-metadata-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-numbered-ranged-repeat-group-lower-bound-warm-str",
    ): ("ranged-repeat-numbered-group-module-search-lower-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str",
    ): ("ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-compile-named-ranged-repeat-group-warm-str",
    ): ("ranged-repeat-named-group-compile-metadata-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-named-ranged-repeat-group-upper-bound-warm-str",
    ): ("ranged-repeat-named-group-module-search-upper-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str",
    ): ("ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS = frozenset(
    {
        "module-sub-template-nested-grouped-alternation-warm-gap",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    }
)
EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_boundary.py",
        "module-compile-grouped-alternation-cold-str",
    ): ("grouped-alternation-compile-metadata-str",),
    (
        "grouped_alternation_boundary.py",
        "module-search-grouped-alternation-warm-str",
    ): ("grouped-alternation-module-search-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-fullmatch-grouped-alternation-purged-str",
    ): ("grouped-alternation-pattern-fullmatch-str",),
    (
        "grouped_alternation_boundary.py",
        "module-compile-named-grouped-alternation-warm-str",
    ): ("named-grouped-alternation-compile-metadata-str",),
    (
        "grouped_alternation_boundary.py",
        "module-search-named-grouped-alternation-warm-str",
    ): ("named-grouped-alternation-module-search-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-fullmatch-named-grouped-alternation-purged-str",
    ): ("named-grouped-alternation-pattern-fullmatch-str",),
    (
        "grouped_alternation_boundary.py",
        "module-sub-template-nested-grouped-alternation-warm-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-wrapper-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    ),
}
EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_boundary.py",
        "module-sub-template-nested-grouped-alternation-warm-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-wrapper-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    ),
}

EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS = frozenset(
    {
        "module-sub-template-nested-grouped-alternation-cold-gap",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    }
)
EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-grouped-alternation-warm-str",
    ): ("module-sub-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-subn-template-grouped-alternation-warm-str",
    ): ("module-subn-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-sub-template-grouped-alternation-purged-str",
    ): ("pattern-sub-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-grouped-alternation-purged-str",
    ): ("pattern-subn-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-named-grouped-alternation-warm-str",
    ): ("module-sub-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-subn-template-named-grouped-alternation-warm-str",
    ): ("module-subn-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-sub-template-named-grouped-alternation-purged-str",
    ): ("pattern-sub-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-grouped-alternation-purged-str",
    ): ("pattern-subn-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-nested-grouped-alternation-cold-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-outer-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    ),
}
EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-nested-grouped-alternation-cold-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-outer-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    ),
}

EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS = (
    "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
    "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
    "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
    "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
    "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
    "module-search-numbered-open-ended-group-conditional-warm-gap",
    "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
    "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
    "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
)

EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS = {
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-alternation-cold-str",
    ): ("open-ended-quantified-group-alternation-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
    ): ("open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-alternation-warm-str",
    ): ("open-ended-quantified-group-alternation-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str",
    ): ("open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
    ): ("open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-alternation-cold-bytes",
    ): ("open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-alternation-warm-bytes",
    ): ("open-ended-quantified-group-alternation-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-conditional-cold-str",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-cold-gap",
    ): (
        "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-conditional-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-conditional-warm-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-conditional-cold-bytes",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-conditional-warm-bytes",
    ): ("open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str",
    ): (
        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str",
    ): (
        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-backtracking-heavy-warm-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",),
}

OPEN_ENDED_DIRECT_PARITY_BYTES_CASES = (
    *OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
)


def _compile_proxy_signature(
    pattern: str | bytes,
    *,
    flags: int,
    text_model: str,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    return ("module.compile", pattern, (), (), flags, text_model)


def _compile_proxy_correctness_case_signature(
    case: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if case.operation != "compile":
        return None
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return _compile_proxy_signature(
        pattern,
        flags=case.flags or 0,
        text_model=case.text_model or "str",
    )


def _compile_proxy_workload_signature(
    workload: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return _compile_proxy_signature(
        pattern,
        flags=workload.flags,
        text_model=workload.text_model,
    )


def _is_compile_proxy_workload(workload: Any) -> bool:
    return workload.operation in {"compile", "module.compile"}


def _optional_group_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.helper != "search":
        return None

    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"
    return (
        "module.search",
        None,
        freeze_signature_value(case.serialized_args()),
        kwargs_signature,
        flags,
        text_model,
    )


def _optional_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation != "module.search":
        raise AssertionError(
            "unexpected optional-group benchmark workload operation "
            f"{workload.operation!r}"
        )

    return (
        "module.search",
        None,
        freeze_signature_value([workload.pattern, workload.haystack]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_optional_group_conditional_workload(workload: Any) -> bool:
    return workload.workload_id == OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID


def _nested_group_correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _nested_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            (workload.pattern, workload.haystack),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            workload.pattern,
            (workload.haystack,),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected nested-group workload operation {workload.operation!r}"
    )


def _is_measured_nested_group_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS


def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return (
            "module.compile",
            case.pattern_payload(),
            (),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern_payload(),
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern_payload(),
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            freeze_signature_value(
                [
                    workload.pattern_payload(),
                    workload.haystack_payload(),
                ]
            ),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            workload.pattern_payload(),
            freeze_signature_value([workload.haystack_payload()]),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected counted-repeat benchmark workload operation {workload.operation!r}"
    )


def _is_non_alternation_counted_repeat_workload(workload: Any) -> bool:
    return workload.operation in {
        "module.compile",
        "module.search",
        "pattern.fullmatch",
    } and "|" not in workload.pattern


def _is_non_special_open_ended_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS


def _grouped_alternation_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper in {"search", "sub", "subn"}:
        return (
            f"module.{case.helper}",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"fullmatch", "sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ()
    if workload.operation == "module.search":
        return freeze_signature_value([workload.pattern, workload.haystack])
    if workload.operation == "pattern.fullmatch":
        return freeze_signature_value([workload.haystack])
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"module.search", "module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.fullmatch", "pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_replacement_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_replacement_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
    elif workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
    else:
        raise AssertionError(
            "unexpected grouped-alternation replacement workload operation "
            f"{workload.operation!r}"
        )

    if workload.count:
        args.append(workload.count)
    return freeze_signature_value(args)


def _grouped_alternation_replacement_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_replacement_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_replacement_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        "unexpected grouped-alternation replacement workload operation "
        f"{workload.operation!r}"
    )


def _include_all_workloads(_: Any) -> bool:
    return True


@cache
def _manifest_workloads_by_id(manifest_path: pathlib.Path) -> dict[str, Any]:
    return {
        workload.workload_id: workload for workload in load_manifest(manifest_path).workloads
    }


def _definition_workloads_by_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[str, Any]:
    workloads_by_id: dict[str, Any] = {}
    for manifest_path in definition.manifest_paths:
        workloads_by_id.update(_manifest_workloads_by_id(manifest_path))
    return workloads_by_id


@cache
def _direct_parity_case_ids_by_signature(
    supplemental_cases: tuple[Any, ...],
) -> dict[tuple[str, bytes, bytes], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[str, bytes, bytes], list[str]] = {}

    for case in supplemental_cases:
        for haystack in case.search_matches + case.search_misses:
            case_ids_by_signature.setdefault(
                ("module.search", case.pattern, haystack),
                [],
            ).append(case.id)
        for haystack in case.fullmatch_matches + case.fullmatch_misses:
            case_ids_by_signature.setdefault(
                ("pattern.fullmatch", case.pattern, haystack),
                [],
            ).append(case.id)

    return {
        signature: tuple(case_ids)
        for signature, case_ids in case_ids_by_signature.items()
    }


def _manual_expected_result(workload: Any) -> object:
    pattern = workload.pattern_payload()
    re.purge()
    try:
        if workload.operation == "module.compile":
            return re.compile(pattern, workload.flags)
        if workload.operation == "module.search":
            return re.search(pattern, workload.haystack_payload(), workload.flags)
        if workload.operation == "pattern.fullmatch":
            compiled = re.compile(pattern, workload.flags)
            return compiled.fullmatch(workload.haystack_payload())
        if workload.operation == "module.sub":
            return re.sub(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "module.subn":
            return re.subn(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "pattern.sub":
            compiled = re.compile(pattern, workload.flags)
            return compiled.sub(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
        if workload.operation == "pattern.subn":
            compiled = re.compile(pattern, workload.flags)
            return compiled.subn(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
    finally:
        re.purge()

    raise AssertionError(
        f"unexpected special-unanchored benchmark workload operation {workload.operation!r}"
    )


STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="compile-proxy",
        manifest_paths=(
            COMPILE_MATRIX_MANIFEST_PATH,
            REGRESSION_MATRIX_MANIFEST_PATH,
        ),
        expected_anchor_case_ids=EXPECTED_COMPILE_ANCHOR_CASE_IDS,
        include_workload=_is_compile_proxy_workload,
        correctness_case_signature=_compile_proxy_correctness_case_signature,
        workload_signature=_compile_proxy_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS,
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS,
        include_workload=_is_measured_nested_group_workload,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_paths=(EXACT_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_paths=(RANGED_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_paths=(GROUPED_ALTERNATION_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_paths=(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS
        ),
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="open-ended-grouped-alternation",
        manifest_paths=(OPEN_ENDED_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS,
        include_workload=_is_non_special_open_ended_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS
        ),
        direct_parity_supplemental_cases=OPEN_ENDED_DIRECT_PARITY_BYTES_CASES,
        run_special_unanchored_result_parity=True,
    ),
)

STANDARD_BENCHMARK_MANIFEST_DEFINITIONS = tuple(
    (definition, manifest_path)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    for manifest_path in definition.manifest_paths
)
STANDARD_BENCHMARK_MANIFEST_IDS = [
    f"{definition.name}:{manifest_path.name}"
    for definition, manifest_path in STANDARD_BENCHMARK_MANIFEST_DEFINITIONS
]
STANDARD_BENCHMARK_LEGACY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_legacy_anchor_case_ids
)
STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_callback_result_parity
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_special_unanchored_workload_ids
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS
    if definition.direct_parity_supplemental_cases
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES = tuple(
    (definition, workload_id)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_special_unanchored_result_parity
    for workload_id in definition.expected_special_unanchored_workload_ids
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS = [
    f"{definition.name}:{workload_id}"
    for definition, workload_id in STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES
]


def _expected_workload_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return tuple(
        workload_id
        for (manifest_name, workload_id), _ in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    )


def _expected_anchor_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchor_case_ids = (
        definition.expected_anchor_case_ids
        if expected_anchor_case_ids is None
        else expected_anchor_case_ids
    )
    return {
        (manifest_name, workload_id): case_ids
        for (manifest_name, workload_id), case_ids in anchor_case_ids.items()
        if manifest_name == manifest_path.name
    }


def _anchored_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=definition.include_workload,
    )


def _anchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            _anchored_case_ids_for_manifest(definition, manifest_path)
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=definition.include_workload,
    )


def _all_unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
    )


def _expected_callback_anchor_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    if definition.callback_anchor_case_ids:
        return definition.callback_anchor_case_ids
    return definition.expected_anchor_case_ids


def _expected_anchored_pairs(
    definition: StandardBenchmarkAnchorContractDefinition,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> tuple[Any, ...]:
    anchored_pairs = []
    for manifest_path in definition.manifest_paths:
        manifest_anchor_case_ids = _expected_anchor_case_ids_for_manifest(
            definition,
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
        )
        if not manifest_anchor_case_ids:
            continue
        anchored_pairs.extend(
            expected_anchored_workload_case_pairs(
                manifest_path,
                expected_anchor_case_ids=manifest_anchor_case_ids,
                include_workload=definition.include_workload,
            )
        )
    return tuple(anchored_pairs)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
)
def test_standard_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    workloads = load_manifest(manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_excluded_workload_ids
    } == definition.expected_excluded_workload_ids
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_workload_ids
    assert tuple(
        workload.workload_id
        for workload in workloads
        if definition.include_workload(workload)
    ) == _expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
)
def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert _unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_special_unanchored_workloads_stay_explicit(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert tuple(
        workload_id
        for manifest_path in definition.manifest_paths
        for workload_id in _all_unanchored_case_ids(definition, manifest_path)
    ) == definition.expected_special_unanchored_workload_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    workloads_by_id = _definition_workloads_by_id(definition)
    direct_parity_case_ids = _direct_parity_case_ids_by_signature(
        definition.direct_parity_supplemental_cases
    )
    uncovered_workload_ids: list[str] = []

    for workload_id in definition.expected_special_unanchored_workload_ids:
        workload = workloads_by_id[workload_id]
        if workload.text_model != "bytes":
            continue
        if workload.operation not in {"module.search", "pattern.fullmatch"}:
            raise AssertionError(
                "expected bytes special-unanchored workload to stay on a direct-parity "
                f"search/fullmatch path, got {workload.operation!r}"
            )

        signature = (
            workload.operation,
            workload.pattern_payload(),
            workload.haystack_payload(),
        )
        case_ids = direct_parity_case_ids.get(signature)
        if case_ids is None:
            uncovered_workload_ids.append(workload_id)
            continue

        assert len(case_ids) == 1

    assert uncovered_workload_ids == []


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_LEGACY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in _anchored_case_ids(definition).items()
        if key[1] in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workload_callbacks_match_anchor_case_results(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(
        _expected_anchored_pairs(
            definition,
            expected_anchor_case_ids=_expected_callback_anchor_case_ids(definition),
        )
    )


@pytest.mark.parametrize(
    ("definition", "workload_id"),
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES,
    ids=STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS,
)
def test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch(
    definition: StandardBenchmarkAnchorContractDefinition,
    workload_id: str,
) -> None:
    workload = _definition_workloads_by_id(definition)[workload_id]
    assert_benchmark_workload_matches_expected_result(
        workload,
        _manual_expected_result(workload),
    )


def test_freeze_signature_value_canonicalizes_nested_mappings_and_lists() -> None:
    value = {
        "b": [2, {"d": 4, "c": [5, 6]}],
        "a": {"y": 1, "x": 0},
    }

    assert support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
    )


def test_published_case_ids_by_signature_groups_duplicate_case_ids(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest = _synthetic_manifest(
        cases=(
            _synthetic_case("case-b", ("shared",)),
            _synthetic_case("case-a", ("shared",)),
            _synthetic_case("case-c", ("unique",)),
            _synthetic_case("ignored", None),
        )
    )
    monkeypatch.setattr(support, "published_fixture_manifests", lambda: (manifest,))

    observed = support.published_case_ids_by_signature(lambda case: case.signature)

    assert observed == {
        ("shared",): ("case-a", "case-b"),
        ("unique",): ("case-c",),
    }


def test_anchored_and_unanchored_workload_helpers_follow_signatures_and_filters(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
    )
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(workloads=workloads),
    )

    anchor_case_ids = {("shared",): ("case-a", "case-b")}
    workload_signature = lambda workload: workload.signature
    include_workload = lambda workload: workload.include

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
        include_workload=include_workload,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a", "case-b"),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
        include_workload=include_workload,
    ) == ("unanchored",)


def test_expected_anchored_workload_case_pairs_return_matching_objects(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = SimpleNamespace(case_id="case-1")
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(workloads=(workload,)),
    )
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})

    anchored_pairs = support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    )

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case


def test_manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
    )
    case = SimpleNamespace(case_id="case-1")
    load_calls: list[pathlib.Path] = []

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        load_calls.append(path)
        return _synthetic_manifest(workloads=workloads)

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})

    anchor_case_ids = {("shared",): ("case-1",)}
    workload_signature = lambda workload: workload.signature

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-1",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
    ) == ("unanchored",)
    assert support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    ) == (
        support.AnchoredWorkloadCasePair(
            manifest_name="synthetic_boundary.py",
            workload_id="anchored",
            case_id="case-1",
            workload=workloads[0],
            case=case,
        ),
    )
    assert load_calls == [manifest_path]


def test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {"case-1": SimpleNamespace(case_id="case-1")},
    )

    with pytest.raises(AssertionError, match="does not match"):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("other_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_multiple_case_ids(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {
            "case-1": SimpleNamespace(case_id="case-1"),
            "case-2": SimpleNamespace(case_id="case-2"),
        },
    )

    with pytest.raises(
        AssertionError,
        match="expected exactly one published correctness case",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1", "case-2"),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_missing_workload(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {"case-1": SimpleNamespace(case_id="case-1")},
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored workload 'missing' to be in scope",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "missing"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_unpublished_case(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {})

    with pytest.raises(
        AssertionError,
        match=r"expected anchored correctness case 'case-1' to be published",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_assert_anchored_workload_case_result_parity_delegates_expected_values(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(
        support,
        "run_correctness_case_with_cpython",
        lambda case: f"expected:{case.case_id}",
    )
    monkeypatch.setattr(
        support,
        "assert_benchmark_workload_matches_expected_result",
        lambda workload, expected: calls.append((workload, expected)),
    )

    support.assert_anchored_workload_case_result_parity((pair,))

    assert calls == [(workload, "expected:case-1")]
