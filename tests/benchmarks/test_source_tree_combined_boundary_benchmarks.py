from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from tests.benchmarks.benchmark_expectations import (
    representative_measured_workload_ids,
    run_source_tree_benchmark_scorecard,
    source_tree_combined_case,
    source_tree_combined_target_manifest_ids,
)
from tests.report_assertions import (
    assert_benchmark_manifest_contract,
    assert_benchmark_workload_contract,
    assert_source_tree_benchmark_contract,
    find_manifest_record,
    find_workload_document,
    find_workload_record,
)

WIDER_RANGED_REPEAT_MANIFEST_ID = "wider-ranged-repeat-quantified-group-boundary"
NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID = "nested-group-callable-replacement-boundary"
NESTED_GROUP_ALTERNATION_MANIFEST_ID = "nested-group-alternation-boundary"
NESTED_GROUP_CALLABLE_REPLACEMENT_ALTERNATION_WORKLOAD_IDS = (
    "module-sub-callable-nested-group-alternation-cold-gap",
    "pattern-subn-callable-numbered-nested-group-alternation-c-branch-first-match-only-purged-str",
    "module-sub-callable-named-nested-group-alternation-c-branch-warm-str",
    "pattern-subn-callable-named-nested-group-alternation-b-branch-first-match-only-purged-str",
)
NESTED_GROUP_CALLABLE_REPLACEMENT_ALTERNATION_PATTERNS = {
    r"a((b|c))d",
    r"a(?P<outer>(?P<inner>b|c))d",
}
NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_ALTERNATION_WORKLOAD_IDS = (
    "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-str",
    "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-str",
    "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
    "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-str",
)
NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_ALTERNATION_PATTERNS = {
    r"a((b|c)+)d",
    r"a(?P<outer>(?P<inner>b|c)+)d",
}
NESTED_GROUP_CALLABLE_REPLACEMENT_BRANCH_LOCAL_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-str",
    "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
    "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-str",
    "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
)
NESTED_GROUP_CALLABLE_REPLACEMENT_BRANCH_LOCAL_PATTERNS = {
    r"a((b|c))\2d",
    r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
}
NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS = (
    "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
    "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
    "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-str",
    "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
)
NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_PATTERNS = {
    r"a((b|c)+)\2d",
    r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
}
NESTED_GROUP_CALLABLE_REPLACEMENT_BROADER_RANGE_BRANCH_LOCAL_WORKLOAD_IDS = (
    "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
    "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-str",
    "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
    "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
)
NESTED_GROUP_CALLABLE_REPLACEMENT_BROADER_RANGE_BRANCH_LOCAL_PATTERNS = {
    r"a((b|c){1,4})\2d",
    r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
}
CALLABLE_REPLACEMENT_FORMER_GAP_CASES = (
    {
        "manifest_id": "grouped-alternation-callable-replacement-boundary",
        "expected_workload_ids": (
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
        "expected_patterns": {
            r"a((b|c))d",
            r"a(?P<outer>(b|c))d",
        },
        "expected_operations": {
            "module.sub",
            "pattern.subn",
        },
        "expected_haystacks": {
            "abdacd",
            "acdabd",
        },
        "required_categories": {
            "alternation",
            "replacement",
            "callable",
            "gap",
        },
    },
    {
        "manifest_id": "nested-group-callable-replacement-boundary",
        "expected_workload_ids": (
            "module-sub-callable-nested-group-alternation-cold-gap",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
        ),
        "expected_patterns": {
            r"a((b|c))d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        "expected_operations": {
            "module.sub",
            "pattern.subn",
        },
        "expected_haystacks": {
            "abdacd",
            "zzabcbcdabcbcdzz",
        },
        "required_categories": {
            "nested-group",
            "replacement",
            "callable",
        },
    },
)
NESTED_GROUP_ALTERNATION_NON_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS = (
    "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
    "module-compile-named-nested-group-branch-local-backreference-warm-str",
    "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
)
NESTED_GROUP_ALTERNATION_NON_QUANTIFIED_BRANCH_LOCAL_PATTERNS = {
    r"a((b|c))\2d",
    r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
}
NESTED_GROUP_ALTERNATION_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS = (
    "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
    "module-compile-named-quantified-nested-group-branch-local-backreference-warm-str",
    "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str",
)
NESTED_GROUP_ALTERNATION_QUANTIFIED_BRANCH_LOCAL_PATTERNS = {
    r"a((b|c)+)\2d",
    r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
}
NESTED_GROUP_ALTERNATION_BROADER_RANGE_BRANCH_LOCAL_WORKLOAD_IDS = (
    "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
    "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str",
    "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str",
)
NESTED_GROUP_ALTERNATION_BROADER_RANGE_BRANCH_LOCAL_PATTERNS = {
    r"a((b|c){1,4})\2d",
    r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
}
WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS = (
    "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
    "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
    "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
    "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
    "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
)
WIDER_RANGED_REPEAT_PATTERN_GROUPS = (
    {
        "label": "nested broader-range grouped alternation",
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
        "label": "nested broader-range grouped conditional",
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
        "pattern_haystacks": (
            "abcbcdede",
            "adedededede",
        ),
    },
    {
        "label": "nested broader-range grouped backtracking-heavy",
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
        "pattern_haystacks": (
            "abcbccd",
            "abccbcd",
            "abcbccbccbcd",
        ),
    },
)


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_combined_source_tree_boundary_scorecards(self) -> None:
        for target_manifest_id in source_tree_combined_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = source_tree_combined_case(target_manifest_id)
                manifest_expectation = case["manifest_expectation"]
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    case["manifest_paths"],
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case["expected_phase"],
                    expected_runner_version=case["expected_runner_version"],
                    expected_adapter=case["expected_adapter"],
                    expected_manifest_documents=case["manifest_documents"],
                    expected_manifest_paths=case["expected_manifest_paths"],
                    expected_selection_mode=case["selection_mode"],
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case["expected_summary"])

                manifest_id = case["manifest_id"]
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = find_manifest_record(scorecard, manifest_id)
                assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest_document=case["target_manifest"],
                    manifest_path=case["manifest_path"],
                    known_gap_count=manifest_expectation["known_gap_count"],
                    selection_mode=case["selection_mode"],
                    selected_workload_ids=case["selected_workload_ids_by_manifest"][manifest_id],
                )

                representative_ids = representative_measured_workload_ids(
                    scorecard,
                    case["target_manifest"],
                    extra_workload_ids=manifest_expectation["representative_measured_workload_ids"],
                )
                representative_gap_ids = set(
                    manifest_expectation["representative_known_gap_workload_ids"]
                )
                representative_ids.extend(manifest_expectation["representative_known_gap_workload_ids"])

                seen_ids: set[str] = set()
                for workload_id in representative_ids:
                    if workload_id in seen_ids:
                        continue
                    seen_ids.add(workload_id)
                    expected_status = (
                        "unimplemented"
                        if workload_id in representative_gap_ids
                        else "measured"
                    )
                    assert_benchmark_workload_contract(
                        self,
                        find_workload_record(scorecard, workload_id),
                        manifest_id=manifest_id,
                        workload_document=find_workload_document(case["target_manifest"], workload_id),
                        expected_status=expected_status,
                    )

    def test_nested_group_alternation_manifest_covers_non_quantified_branch_local_backreference_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_ALTERNATION_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_ALTERNATION_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        branch_local_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "branch-local-backreferences" in workload["syntax_features"]
            and "quantifiers" not in workload["syntax_features"]
        ]
        self._assert_nested_group_alternation_branch_local_rows(
            case["target_manifest"],
            scorecard,
            branch_local_rows=branch_local_rows,
            expected_workload_ids=NESTED_GROUP_ALTERNATION_NON_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS,
            expected_patterns=NESTED_GROUP_ALTERNATION_NON_QUANTIFIED_BRANCH_LOCAL_PATTERNS,
            expected_haystacks={"zzabbdzz", "accd"},
        )

    def test_nested_group_alternation_manifest_covers_quantified_branch_local_backreference_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_ALTERNATION_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_ALTERNATION_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        quantified_branch_local_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "branch-local-backreferences" in workload["syntax_features"]
            and "quantifiers" in workload["syntax_features"]
            and "counted-repeats" not in workload["syntax_features"]
        ]
        self._assert_nested_group_alternation_branch_local_rows(
            case["target_manifest"],
            scorecard,
            branch_local_rows=quantified_branch_local_rows,
            expected_workload_ids=NESTED_GROUP_ALTERNATION_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS,
            expected_patterns=NESTED_GROUP_ALTERNATION_QUANTIFIED_BRANCH_LOCAL_PATTERNS,
            expected_haystacks={"zzabbdzz", "abccd"},
        )

    def test_nested_group_alternation_manifest_covers_broader_range_branch_local_backreference_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_ALTERNATION_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_ALTERNATION_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        broader_range_branch_local_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "branch-local-backreferences" in workload["syntax_features"]
            and "counted-repeats" in workload["syntax_features"]
        ]
        self._assert_nested_group_alternation_branch_local_rows(
            case["target_manifest"],
            scorecard,
            branch_local_rows=broader_range_branch_local_rows,
            expected_workload_ids=NESTED_GROUP_ALTERNATION_BROADER_RANGE_BRANCH_LOCAL_WORKLOAD_IDS,
            expected_patterns=NESTED_GROUP_ALTERNATION_BROADER_RANGE_BRANCH_LOCAL_PATTERNS,
            expected_haystacks={"zzabbdzz", "acccccd"},
        )

    def _assert_nested_group_alternation_branch_local_rows(
        self,
        manifest_document: dict[str, object],
        scorecard: dict[str, object],
        *,
        branch_local_rows: list[dict[str, object]],
        expected_workload_ids: tuple[str, ...],
        expected_patterns: set[str],
        expected_haystacks: set[str],
    ) -> None:
        self.assertEqual(
            tuple(workload["id"] for workload in branch_local_rows),
            expected_workload_ids,
        )
        self.assertEqual(
            {workload["operation"] for workload in branch_local_rows},
            {"module.compile", "module.search", "pattern.fullmatch"},
        )
        self.assertEqual(
            {workload["pattern"] for workload in branch_local_rows},
            expected_patterns,
        )
        self.assertEqual(
            {
                str(workload["haystack"])
                for workload in branch_local_rows
                if workload.get("haystack") is not None
            },
            expected_haystacks,
        )

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == NESTED_GROUP_ALTERNATION_MANIFEST_ID
            and workload["id"] in expected_workload_ids
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            set(expected_workload_ids),
        )

        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=NESTED_GROUP_ALTERNATION_MANIFEST_ID,
                    workload_document=find_workload_document(
                        manifest_document,
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_nested_group_callable_replacement_manifest_covers_nested_alternation_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        alternation_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "alternation" in workload["syntax_features"]
            and "callable-replacement" in workload["syntax_features"]
            and "branch-local-backreferences" not in workload["syntax_features"]
            and "quantifiers" not in workload["syntax_features"]
        ]
        self.assertEqual(
            tuple(workload["id"] for workload in alternation_rows),
            NESTED_GROUP_CALLABLE_REPLACEMENT_ALTERNATION_WORKLOAD_IDS,
        )
        self.assertEqual(
            {workload["pattern"] for workload in alternation_rows},
            NESTED_GROUP_CALLABLE_REPLACEMENT_ALTERNATION_PATTERNS,
        )
        self.assertEqual(
            {workload["operation"] for workload in alternation_rows},
            {"module.sub", "pattern.subn"},
        )
        self.assertEqual(
            {
                str(workload["haystack"])
                for workload in alternation_rows
                if workload.get("haystack") is not None
            },
            {"abdacd", "acdabd", "acd"},
        )
        for workload in alternation_rows:
            for category in ("nested-group", "alternation", "replacement", "callable"):
                self.assertIn(category, workload["categories"])

        for workload_id in NESTED_GROUP_CALLABLE_REPLACEMENT_ALTERNATION_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_nested_group_callable_replacement_manifest_covers_quantified_nested_alternation_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        quantified_alternation_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "alternation" in workload["syntax_features"]
            and "callable-replacement" in workload["syntax_features"]
            and "branch-local-backreferences" not in workload["syntax_features"]
            and "quantifiers" in workload["syntax_features"]
        ]
        self.assertEqual(
            tuple(workload["id"] for workload in quantified_alternation_rows),
            NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_ALTERNATION_WORKLOAD_IDS,
        )
        self.assertEqual(
            {workload["pattern"] for workload in quantified_alternation_rows},
            NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_ALTERNATION_PATTERNS,
        )
        self.assertEqual(
            {workload["operation"] for workload in quantified_alternation_rows},
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        )
        self.assertEqual(
            {
                str(workload["haystack"])
                for workload in quantified_alternation_rows
                if workload.get("haystack") is not None
            },
            {"zzabdzz", "zzabccdacbbdzz", "zzabccdzz"},
        )
        for workload in quantified_alternation_rows:
            for category in (
                "nested-group",
                "alternation",
                "replacement",
                "callable",
                "quantified",
            ):
                self.assertIn(category, workload["categories"])

        for workload_id in NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_ALTERNATION_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_nested_group_callable_replacement_manifest_covers_branch_local_backreference_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        branch_local_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "branch-local-backreferences" in workload["syntax_features"]
            and "callable-replacement" in workload["syntax_features"]
            and "quantifiers" not in workload["syntax_features"]
        ]
        self.assertEqual(
            tuple(workload["id"] for workload in branch_local_rows),
            NESTED_GROUP_CALLABLE_REPLACEMENT_BRANCH_LOCAL_WORKLOAD_IDS,
        )
        self.assertEqual(
            {workload["pattern"] for workload in branch_local_rows},
            NESTED_GROUP_CALLABLE_REPLACEMENT_BRANCH_LOCAL_PATTERNS,
        )
        self.assertEqual(
            {workload["operation"] for workload in branch_local_rows},
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        )
        self.assertEqual(
            {
                str(workload["haystack"])
                for workload in branch_local_rows
                if workload.get("haystack") is not None
            },
            {"abbd", "abbdaccd", "accd", "accdabbd"},
        )
        for workload in branch_local_rows:
            for category in (
                "nested-group",
                "alternation",
                "replacement",
                "callable",
                "branch-local",
            ):
                self.assertIn(category, workload["categories"])

        for workload_id in NESTED_GROUP_CALLABLE_REPLACEMENT_BRANCH_LOCAL_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_nested_group_callable_replacement_manifest_covers_quantified_branch_local_backreference_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        quantified_branch_local_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "branch-local-backreferences" in workload["syntax_features"]
            and "callable-replacement" in workload["syntax_features"]
            and "quantifiers" in workload["syntax_features"]
            and "counted-repeats" not in workload["syntax_features"]
            and "ranged-repeats" not in workload["syntax_features"]
        ]
        self.assertEqual(
            tuple(workload["id"] for workload in quantified_branch_local_rows),
            NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS,
        )
        self.assertEqual(
            {workload["pattern"] for workload in quantified_branch_local_rows},
            NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_PATTERNS,
        )
        self.assertEqual(
            {workload["operation"] for workload in quantified_branch_local_rows},
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        )
        self.assertEqual(
            {
                str(workload["haystack"])
                for workload in quantified_branch_local_rows
                if workload.get("haystack") is not None
            },
            {"abbd", "abbbdaccd", "zzabccdzz", "zzaccdabbbdzz"},
        )
        for workload in quantified_branch_local_rows:
            for category in (
                "nested-group",
                "alternation",
                "replacement",
                "callable",
                "branch-local",
                "quantified",
            ):
                self.assertIn(category, workload["categories"])

        for workload_id in (
            NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_WORKLOAD_IDS
        ):
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_nested_group_callable_replacement_manifest_covers_broader_range_branch_local_backreference_slice(
        self,
    ) -> None:
        case = source_tree_combined_case(NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)

        broader_range_branch_local_rows = [
            workload
            for workload in case["target_manifest"]["workloads"]
            if "branch-local-backreferences" in workload["syntax_features"]
            and "callable-replacement" in workload["syntax_features"]
            and "quantifiers" in workload["syntax_features"]
            and "counted-repeats" in workload["syntax_features"]
            and "ranged-repeats" in workload["syntax_features"]
        ]
        self.assertEqual(
            tuple(workload["id"] for workload in broader_range_branch_local_rows),
            NESTED_GROUP_CALLABLE_REPLACEMENT_BROADER_RANGE_BRANCH_LOCAL_WORKLOAD_IDS,
        )
        self.assertEqual(
            {workload["pattern"] for workload in broader_range_branch_local_rows},
            NESTED_GROUP_CALLABLE_REPLACEMENT_BROADER_RANGE_BRANCH_LOCAL_PATTERNS,
        )
        self.assertEqual(
            {workload["operation"] for workload in broader_range_branch_local_rows},
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        )
        self.assertEqual(
            {
                str(workload["haystack"])
                for workload in broader_range_branch_local_rows
                if workload.get("haystack") is not None
            },
            {"abbd", "abcbccdabbd", "zzacccccdzz", "zzacccccdabbbdzz"},
        )
        for workload in broader_range_branch_local_rows:
            for category in (
                "nested-group",
                "alternation",
                "replacement",
                "callable",
                "branch-local",
                "quantified",
                "ranged-repeat",
                "counted-repeat",
                "broader-range",
            ):
                self.assertIn(category, workload["categories"])

        for workload_id in (
            NESTED_GROUP_CALLABLE_REPLACEMENT_BROADER_RANGE_BRANCH_LOCAL_WORKLOAD_IDS
        ):
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_callable_replacement_former_gap_rows_are_measured_in_combined_suite(
        self,
    ) -> None:
        for case_definition in CALLABLE_REPLACEMENT_FORMER_GAP_CASES:
            manifest_id = case_definition["manifest_id"]
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

                manifest_summary = scorecard["manifests"][manifest_id]
                self.assertEqual(manifest_summary["known_gap_count"], 0)

                former_gap_rows = [
                    workload
                    for workload in case["target_manifest"]["workloads"]
                    if workload["id"].endswith("gap")
                    and "callable-replacement" in workload["syntax_features"]
                ]
                self.assertEqual(
                    tuple(workload["id"] for workload in former_gap_rows),
                    case_definition["expected_workload_ids"],
                )
                self.assertEqual(
                    {workload["pattern"] for workload in former_gap_rows},
                    case_definition["expected_patterns"],
                )
                self.assertEqual(
                    {workload["operation"] for workload in former_gap_rows},
                    case_definition["expected_operations"],
                )
                self.assertEqual(
                    {str(workload["haystack"]) for workload in former_gap_rows},
                    case_definition["expected_haystacks"],
                )
                for workload in former_gap_rows:
                    for category in case_definition["required_categories"]:
                        self.assertIn(category, workload["categories"])

                for workload_id in case_definition["expected_workload_ids"]:
                    with self.subTest(workload_id=workload_id):
                        assert_benchmark_workload_contract(
                            self,
                            find_workload_record(scorecard, workload_id),
                            manifest_id=manifest_id,
                            workload_document=find_workload_document(
                                case["target_manifest"],
                                workload_id,
                            ),
                            expected_status="measured",
                        )

    def test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite(
        self,
    ) -> None:
        case = source_tree_combined_case(WIDER_RANGED_REPEAT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][WIDER_RANGED_REPEAT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            len(case["target_manifest"]["workloads"]),
        )
        self.assertEqual(
            manifest_summary["workload_count"],
            len(case["target_manifest"]["workloads"]),
        )

        for workload_id in WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=WIDER_RANGED_REPEAT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

        for pattern_group in WIDER_RANGED_REPEAT_PATTERN_GROUPS:
            with self.subTest(group=pattern_group["label"]):
                self._assert_wider_ranged_repeat_pattern_group(
                    case["target_manifest"],
                    scorecard,
                    label=pattern_group["label"],
                    patterns=pattern_group["patterns"],
                    minimum_rows=pattern_group["minimum_rows"],
                    required_operations=pattern_group["required_operations"],
                    required_categories=pattern_group["required_categories"],
                    search_haystacks=pattern_group.get("search_haystacks", ()),
                    search_haystack_substrings=pattern_group.get(
                        "search_haystack_substrings",
                        (),
                    ),
                    pattern_haystacks=pattern_group["pattern_haystacks"],
                )

    def _assert_wider_ranged_repeat_pattern_group(
        self,
        manifest_document: dict[str, object],
        scorecard: dict[str, object],
        *,
        label: str,
        patterns: tuple[str, ...],
        minimum_rows: int,
        required_operations: tuple[str, ...],
        required_categories: tuple[str, ...],
        search_haystacks: tuple[str, ...],
        search_haystack_substrings: tuple[str, ...],
        pattern_haystacks: tuple[str, ...],
    ) -> None:
        manifest_rows = [
            workload
            for workload in manifest_document["workloads"]
            if workload.get("pattern") in patterns
        ]

        self.assertGreaterEqual(
            len(manifest_rows),
            minimum_rows,
            f"expected benchmark rows for the {label} slice",
        )

        for pattern in patterns:
            pattern_rows = [
                workload for workload in manifest_rows if workload["pattern"] == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertTrue(
                set(required_operations).issubset(
                    {workload["operation"] for workload in pattern_rows}
                )
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload["id"]):
                    for category in required_categories:
                        self.assertIn(category, workload["categories"])

        manifest_search_haystacks = {
            str(workload["haystack"])
            for workload in manifest_rows
            if workload["operation"] == "module.search"
        }
        for haystack in search_haystacks:
            self.assertIn(haystack, manifest_search_haystacks)
        for snippet in search_haystack_substrings:
            self.assertTrue(
                any(snippet in haystack for haystack in manifest_search_haystacks),
                f"expected a module.search workload covering {snippet!r}",
            )

        manifest_pattern_haystacks = {
            str(workload["haystack"])
            for workload in manifest_rows
            if workload["operation"] == "pattern.fullmatch"
        }
        for haystack in pattern_haystacks:
            self.assertIn(haystack, manifest_pattern_haystacks)

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == WIDER_RANGED_REPEAT_MANIFEST_ID
            and workload["pattern"] in patterns
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            {workload["id"] for workload in manifest_rows},
        )
        for workload in scorecard_rows:
            with self.subTest(scorecard_workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
