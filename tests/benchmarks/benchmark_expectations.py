from __future__ import annotations


SOURCE_TREE_BOUNDARY_GAP_EXPECTATIONS = {
    "branch-local-backreference-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "collection-replacement-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "compile-matrix": {
        "known_gap_count": 1,
        "representative_known_gap_workload_id": "compile-parser-stress-cold",
    },
    "conditional-group-exists-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap"
        ),
    },
    "conditional-group-exists-empty-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "conditional-group-exists-empty-yes-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "conditional-group-exists-fully-empty-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "conditional-group-exists-no-else-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "exact-repeat-quantified-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_id": (
            "module-search-numbered-broader-ranged-repeat-group-cold-gap"
        ),
    },
    "grouped-alternation-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-sub-template-nested-grouped-alternation-warm-gap"
        ),
    },
    "grouped-alternation-callable-replacement-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-sub-callable-nested-grouped-alternation-cold-gap"
        ),
    },
    "grouped-alternation-replacement-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-sub-template-nested-grouped-alternation-cold-gap"
        ),
    },
    "grouped-named-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": "module-search-grouped-segment-cold-gap",
    },
    "grouped-segment-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "literal-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "literal-flag-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": "module-search-ignorecase-ascii-cold-gap",
    },
    "module-boundary": {
        "known_gap_count": 3,
        "representative_known_gap_workload_id": "module-compile-literal-cold",
    },
    "nested-group-alternation-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-search-nested-group-quantified-alternation-cold-gap"
        ),
    },
    "nested-group-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": "module-search-triple-nested-group-cold-gap",
    },
    "nested-group-callable-replacement-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-sub-callable-nested-group-alternation-cold-gap"
        ),
    },
    "nested-group-replacement-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_id": (
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap"
        ),
    },
    "numbered-backreference-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-search-numbered-backreference-segment-cold-gap"
        ),
    },
    "open-ended-quantified-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_id": (
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-gap"
        ),
    },
    "optional-group-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "optional-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_id": (
            "module-search-numbered-optional-group-conditional-cold-gap"
        ),
    },
    "pattern-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "quantified-alternation-boundary": {
        "known_gap_count": 0,
        "representative_known_gap_workload_id": None,
    },
    "ranged-repeat-quantified-group-boundary": {
        "known_gap_count": 1,
        "representative_known_gap_workload_id": (
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap"
        ),
    },
    "regression-matrix": {
        "known_gap_count": 3,
        "representative_known_gap_workload_id": "regression-parser-atomic-lookbehind-cold",
    },
    "wider-ranged-repeat-quantified-group-boundary": {
        "known_gap_count": 2,
        "representative_known_gap_workload_id": (
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap"
        ),
    },
}
