from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import (
    DEFAULT_FIXTURE_PATHS,
    FixtureCase,
    FixtureManifest,
    determine_phase,
    load_fixture_manifest,
)


@lru_cache(maxsize=1)
def build_rebar_extension() -> None:
    subprocess.run(
        ["cargo", "build", "-p", "rebar-cpython"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def run_correctness_scorecard(
    fixture_paths: Iterable[pathlib.Path],
) -> tuple[dict[str, object], dict[str, object]]:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / "correctness.json"
        command = [
            sys.executable,
            "-m",
            "rebar_harness.correctness",
            "--fixtures",
            *(str(path) for path in fixture_paths),
            "--report",
            str(report_path),
        ]
        result = subprocess.run(
            command,
            check=True,
            cwd=REPO_ROOT,
            env={"PYTHONPATH": str(PYTHON_SOURCE)},
            capture_output=True,
            text=True,
        )
        summary = json.loads(result.stdout.strip())
        scorecard = json.loads(report_path.read_text(encoding="utf-8"))
    return summary, scorecard


COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS = {
    "parser-matrix": {
        "representative_case_ids": (
            "str-literal-success",
            "str-inline-unicode-flag-success",
            "str-character-class-ignorecase-success",
            "str-possessive-quantifier-success",
            "str-atomic-group-success",
            "str-fixed-width-lookbehind-success",
            "str-nested-set-warning",
            "str-variable-width-lookbehind-error",
            "bytes-inline-unicode-flag-error",
            "bytes-inline-locale-flag-success",
        ),
    },
    "public-api-surface": {
        "representative_case_ids": (
            "compile-pattern-scaffold-success",
            "purge-noop-success",
            "search-literal-success",
            "escape-success",
        ),
    },
    "match-behavior-smoke": {
        "representative_case_ids": (
            "search-str-success-literal",
            "match-str-no-match",
            "fullmatch-bytes-success-literal",
        ),
    },
    "exported-symbol-surface": {
        "representative_case_ids": (
            "regexflag-type-metadata",
            "error-type-metadata",
            "ascii-constant-value",
            "pattern-type-metadata",
            "pattern-constructor-guard",
        ),
    },
    "pattern-object-surface": {
        "representative_case_ids": (
            "pattern-object-str-metadata",
            "pattern-object-bytes-ignorecase-metadata",
            "pattern-search-literal-success",
        ),
    },
    "module-workflow-surface": {
        "representative_case_ids": (
            "workflow-cache-hit-str",
            "workflow-purge-reset-str",
            "workflow-pattern-search-str",
            "workflow-pattern-fullmatch-bytes",
            "workflow-escape-bytes",
        ),
    },
    "collection-replacement-workflows": {
        "representative_case_ids": (
            "module-finditer-str-repeated",
            "pattern-split-bytes-maxsplit",
            "module-subn-bytes-count",
            "module-sub-template-str",
            "module-sub-callable-str",
            "module-sub-grouping-template",
            "module-findall-nonliteral-str",
        ),
    },
    "literal-flag-workflows": {
        "representative_case_ids": (
            "flag-module-search-ignorecase-str-hit",
            "flag-pattern-fullmatch-ignorecase-str-miss",
            "flag-pattern-match-ignorecase-bytes-hit",
            "flag-cache-distinct-str-normalized",
            "flag-unsupported-inline-flag-search",
            "flag-unsupported-locale-bytes-search",
            "flag-unsupported-nonliteral-ignorecase-search",
        ),
    },
    "grouped-match-workflows": {
        "representative_case_ids": (
            "grouped-module-search-single-capture-str",
            "grouped-pattern-match-single-capture-str",
            "grouped-module-fullmatch-two-capture-gap-str",
        ),
    },
    "named-group-workflows": {
        "representative_case_ids": (
            "named-group-compile-metadata-str",
            "named-group-module-search-metadata-str",
            "named-group-pattern-search-metadata-str",
        ),
    },
    "named-group-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-template-named-group-str",
            "module-subn-template-named-group-str",
            "pattern-sub-template-named-group-str",
            "pattern-subn-template-named-group-str",
        ),
    },
    "named-backreference-workflows": {
        "representative_case_ids": (
            "named-backreference-compile-metadata-str",
            "named-backreference-module-search-str",
            "named-backreference-pattern-search-str",
        ),
    },
    "numbered-backreference-workflows": {
        "representative_case_ids": (
            "numbered-backreference-compile-metadata-str",
            "numbered-backreference-module-search-str",
            "numbered-backreference-pattern-search-str",
        ),
    },
    "grouped-segment-workflows": {
        "representative_case_ids": (
            "grouped-segment-compile-metadata-str",
            "named-grouped-segment-compile-metadata-str",
            "grouped-segment-module-search-str",
            "named-grouped-segment-pattern-fullmatch-str",
        ),
    },
    "nested-group-workflows": {
        "representative_case_ids": (
            "nested-group-compile-metadata-str",
            "named-nested-group-compile-metadata-str",
            "nested-group-module-search-str",
            "named-nested-group-pattern-fullmatch-str",
        ),
    },
    "literal-alternation-workflows": {
        "representative_case_ids": (
            "literal-alternation-compile-metadata-str",
            "literal-alternation-module-search-str",
            "literal-alternation-pattern-fullmatch-str",
        ),
    },
    "grouped-alternation-workflows": {
        "representative_case_ids": (
            "grouped-alternation-compile-metadata-str",
            "named-grouped-alternation-compile-metadata-str",
            "grouped-alternation-module-search-str",
            "named-grouped-alternation-pattern-fullmatch-str",
        ),
    },
    "grouped-alternation-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-template-grouped-alternation-str",
            "module-subn-template-grouped-alternation-str",
            "pattern-sub-template-named-grouped-alternation-str",
            "pattern-subn-template-named-grouped-alternation-str",
        ),
    },
    "grouped-alternation-callable-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-callable-grouped-alternation-str",
            "module-subn-callable-grouped-alternation-str",
            "pattern-sub-callable-named-grouped-alternation-str",
        ),
    },
    "branch-local-backreference-workflows": {
        "representative_case_ids": (
            "branch-local-numbered-backreference-compile-metadata-str",
            "branch-local-numbered-backreference-module-search-str",
            "branch-local-numbered-backreference-pattern-fullmatch-str",
            "branch-local-named-backreference-compile-metadata-str",
            "branch-local-named-backreference-module-search-str",
            "branch-local-named-backreference-pattern-fullmatch-str",
        ),
    },
    "optional-group-workflows": {
        "representative_case_ids": (
            "optional-group-compile-metadata-str",
            "optional-group-module-search-present-str",
            "optional-group-pattern-fullmatch-absent-str",
            "named-optional-group-compile-metadata-str",
            "named-optional-group-module-search-absent-str",
            "named-optional-group-pattern-fullmatch-present-str",
            "systematic-optional-group-numbered-pattern-fullmatch-present-str",
            "systematic-optional-group-named-module-search-present-str",
        ),
    },
    "exact-repeat-quantified-group-workflows": {
        "representative_case_ids": (
            "exact-repeat-numbered-group-compile-metadata-str",
            "exact-repeat-numbered-group-module-search-str",
            "exact-repeat-numbered-group-pattern-fullmatch-str",
            "exact-repeat-named-group-compile-metadata-str",
            "exact-repeat-named-group-module-search-str",
            "exact-repeat-named-group-pattern-fullmatch-str",
        ),
    },
    "exact-repeat-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "exact-repeat-quantified-group-alternation-numbered-compile-metadata-str",
            "exact-repeat-quantified-group-alternation-numbered-module-search-bc-bc-str",
            "exact-repeat-quantified-group-alternation-numbered-module-search-bc-de-str",
            "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-de-de-str",
            "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
            "exact-repeat-quantified-group-alternation-named-compile-metadata-str",
            "exact-repeat-quantified-group-alternation-named-module-search-bc-bc-str",
            "exact-repeat-quantified-group-alternation-named-module-search-bc-de-str",
            "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-de-de-str",
            "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-extra-repetition-str",
        ),
    },
    "ranged-repeat-quantified-group-workflows": {
        "representative_case_ids": (
            "ranged-repeat-numbered-group-compile-metadata-str",
            "ranged-repeat-numbered-group-module-search-lower-bound-str",
            "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
            "ranged-repeat-named-group-compile-metadata-str",
            "ranged-repeat-named-group-module-search-upper-bound-str",
            "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
        ),
    },
    "wider-ranged-repeat-quantified-group-workflows": {
        "representative_case_ids": (
            "wider-ranged-repeat-numbered-group-compile-metadata-str",
            "wider-ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
            "wider-ranged-repeat-named-group-module-search-upper-bound-str",
            "wider-ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
        ),
    },
    "nested-group-alternation-workflows": {
        "representative_case_ids": (
            "nested-group-alternation-compile-metadata-str",
            "named-nested-group-alternation-pattern-fullmatch-str",
        ),
    },
    "nested-group-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-template-nested-group-numbered-str",
            "module-subn-template-nested-group-numbered-str",
            "pattern-sub-template-nested-group-named-str",
            "pattern-subn-template-nested-group-named-str",
        ),
    },
    "quantified-nested-group-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
            "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
            "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
            "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
        ),
    },
    "quantified-nested-group-callable-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
            "module-subn-callable-quantified-nested-group-numbered-first-match-only-str",
            "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str",
            "pattern-subn-callable-quantified-nested-group-named-first-match-only-str",
        ),
    },
    "nested-group-callable-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-callable-nested-group-numbered-str",
            "module-subn-callable-nested-group-numbered-str",
            "pattern-sub-callable-nested-group-named-str",
        ),
    },
    "optional-group-alternation-workflows": {
        "representative_case_ids": (
            "optional-group-alternation-compile-metadata-str",
            "optional-group-alternation-module-search-present-str",
            "optional-group-alternation-pattern-fullmatch-absent-str",
            "named-optional-group-alternation-compile-metadata-str",
            "named-optional-group-alternation-module-search-present-str",
            "named-optional-group-alternation-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-compile-metadata-str",
            "conditional-group-exists-module-search-present-str",
            "conditional-group-exists-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-compile-metadata-str",
            "named-conditional-group-exists-module-search-present-str",
            "named-conditional-group-exists-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-no-else-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-no-else-compile-metadata-str",
            "conditional-group-exists-no-else-module-search-present-str",
            "conditional-group-exists-no-else-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-compile-metadata-str",
            "named-conditional-group-exists-no-else-module-search-present-str",
            "named-conditional-group-exists-no-else-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-empty-else-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-else-compile-metadata-str",
            "conditional-group-exists-empty-else-module-search-present-str",
            "conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-compile-metadata-str",
            "named-conditional-group-exists-empty-else-module-search-present-str",
            "named-conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-empty-yes-else-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-yes-else-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-module-search-present-str",
            "conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-yes-else-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-module-search-present-str",
            "named-conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-fully-empty-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-fully-empty-compile-metadata-str",
            "conditional-group-exists-fully-empty-module-search-present-str",
            "conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-module-search-present-str",
            "named-conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-assertion-diagnostics": {
        "representative_case_ids": (
            "conditional-group-exists-assertion-positive-lookahead-error-str",
            "conditional-group-exists-assertion-negative-lookahead-error-str",
        ),
    },
    "quantified-alternation-workflows": {
        "representative_case_ids": (
            "quantified-alternation-numbered-module-search-lower-bound-str",
            "quantified-alternation-numbered-pattern-fullmatch-second-repetition-str",
            "quantified-alternation-named-compile-metadata-str",
            "quantified-alternation-named-module-search-second-repetition-str",
            "quantified-alternation-named-pattern-fullmatch-lower-bound-str",
        ),
    },
    "quantified-nested-group-alternation-workflows": {
        "representative_case_ids": (
            "quantified-nested-group-alternation-numbered-compile-metadata-str",
            "quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str",
            "quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str",
            "quantified-nested-group-alternation-named-compile-metadata-str",
            "quantified-nested-group-alternation-named-module-search-lower-bound-c-str",
            "quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str",
        ),
    },
    "nested-group-alternation-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
            "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
            "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
            "nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
            "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
            "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
        ),
    },
    "quantified-nested-group-alternation-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
            "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
            "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
            "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
            "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
        ),
    },
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-str",
        ),
    },
}


BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-branch-local-numbered-backreference-compile-metadata-str",
            "conditional-group-exists-branch-local-numbered-backreference-module-search-present-str",
            "conditional-group-exists-branch-local-numbered-backreference-pattern-fullmatch-absent-str",
            "conditional-group-exists-branch-local-named-backreference-compile-metadata-str",
            "conditional-group-exists-branch-local-named-backreference-module-search-present-str",
            "conditional-group-exists-branch-local-named-backreference-pattern-fullmatch-absent-str",
        ),
    },
    "optional-group-alternation-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "optional-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "optional-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
            "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
            "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-absent-group-str",
            "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
            "optional-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "optional-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
            "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
            "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-absent-group-str",
            "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
        ),
    },
    "quantified-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "quantified-branch-local-numbered-backreference-compile-metadata-str",
            "quantified-branch-local-numbered-backreference-module-search-lower-bound-str",
            "quantified-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-str",
            "quantified-branch-local-numbered-backreference-pattern-fullmatch-absent-branch-str",
            "quantified-branch-local-named-backreference-compile-metadata-str",
            "quantified-branch-local-named-backreference-module-search-lower-bound-str",
            "quantified-branch-local-named-backreference-pattern-fullmatch-second-iteration-str",
            "quantified-branch-local-named-backreference-pattern-fullmatch-absent-branch-str",
        ),
    },
}


CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-nested-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-nested-compile-metadata-str",
            "conditional-group-exists-nested-module-search-present-str",
            "conditional-group-exists-nested-module-fullmatch-absent-str",
            "conditional-group-exists-nested-pattern-fullmatch-unreachable-inner-else-str",
            "named-conditional-group-exists-nested-compile-metadata-str",
            "named-conditional-group-exists-nested-module-search-present-str",
            "named-conditional-group-exists-nested-module-fullmatch-absent-str",
            "named-conditional-group-exists-nested-pattern-fullmatch-unreachable-inner-else-str",
        ),
    },
    "conditional-group-exists-no-else-nested-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-no-else-nested-compile-metadata-str",
            "conditional-group-exists-no-else-nested-module-search-present-str",
            "conditional-group-exists-no-else-nested-module-fullmatch-missing-suffix-str",
            "conditional-group-exists-no-else-nested-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-nested-compile-metadata-str",
            "named-conditional-group-exists-no-else-nested-module-search-present-str",
            "named-conditional-group-exists-no-else-nested-module-fullmatch-missing-suffix-str",
            "named-conditional-group-exists-no-else-nested-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-quantified-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-quantified-compile-metadata-str",
            "conditional-group-exists-quantified-module-search-present-str",
            "conditional-group-exists-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
            "named-conditional-group-exists-quantified-compile-metadata-str",
            "named-conditional-group-exists-quantified-module-search-present-str",
            "named-conditional-group-exists-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
        ),
    },
    "conditional-group-exists-no-else-quantified-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-no-else-quantified-compile-metadata-str",
            "conditional-group-exists-no-else-quantified-module-search-present-str",
            "conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
            "named-conditional-group-exists-no-else-quantified-compile-metadata-str",
            "named-conditional-group-exists-no-else-quantified-module-search-present-str",
            "named-conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
        ),
    },
    "conditional-group-exists-empty-else-nested-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-else-nested-compile-metadata-str",
            "conditional-group-exists-empty-else-nested-module-search-present-str",
            "conditional-group-exists-empty-else-nested-module-fullmatch-missing-suffix-str",
            "conditional-group-exists-empty-else-nested-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-nested-compile-metadata-str",
            "named-conditional-group-exists-empty-else-nested-module-search-present-str",
            "named-conditional-group-exists-empty-else-nested-module-fullmatch-missing-suffix-str",
            "named-conditional-group-exists-empty-else-nested-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-empty-else-quantified-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-else-quantified-compile-metadata-str",
            "conditional-group-exists-empty-else-quantified-module-search-present-str",
            "conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
            "named-conditional-group-exists-empty-else-quantified-compile-metadata-str",
            "named-conditional-group-exists-empty-else-quantified-module-search-present-str",
            "named-conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
        ),
    },
    "conditional-group-exists-empty-yes-else-nested-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-yes-else-nested-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-nested-module-search-present-str",
            "conditional-group-exists-empty-yes-else-nested-module-fullmatch-absent-str",
            "conditional-group-exists-empty-yes-else-nested-pattern-fullmatch-absent-failure-str",
            "named-conditional-group-exists-empty-yes-else-nested-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-nested-module-search-present-str",
            "named-conditional-group-exists-empty-yes-else-nested-module-fullmatch-absent-str",
            "named-conditional-group-exists-empty-yes-else-nested-pattern-fullmatch-absent-failure-str",
        ),
    },
    "conditional-group-exists-empty-yes-else-quantified-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
            "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
            "named-conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
            "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
        ),
    },
    "conditional-group-exists-fully-empty-nested-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-fully-empty-nested-compile-metadata-str",
            "conditional-group-exists-fully-empty-nested-module-search-present-str",
            "conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
            "conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
            "named-conditional-group-exists-fully-empty-nested-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-nested-module-search-present-str",
            "named-conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
        ),
    },
    "conditional-group-exists-fully-empty-quantified-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-fully-empty-quantified-compile-metadata-str",
            "conditional-group-exists-fully-empty-quantified-module-fullmatch-present-str",
            "conditional-group-exists-fully-empty-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-fully-empty-quantified-pattern-fullmatch-mixed-str",
            "conditional-group-exists-fully-empty-quantified-pattern-fullmatch-extra-suffix-failure-str",
            "named-conditional-group-exists-fully-empty-quantified-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-quantified-module-fullmatch-present-str",
            "named-conditional-group-exists-fully-empty-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-quantified-pattern-fullmatch-mixed-str",
            "named-conditional-group-exists-fully-empty-quantified-pattern-fullmatch-extra-suffix-failure-str",
        ),
    },
}


CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-no-else-alternation-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-no-else-alternation-compile-metadata-str",
            "conditional-group-exists-no-else-alternation-module-search-first-arm-str",
            "conditional-group-exists-no-else-alternation-module-search-second-arm-str",
            "conditional-group-exists-no-else-alternation-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-alternation-compile-metadata-str",
            "named-conditional-group-exists-no-else-alternation-module-search-first-arm-str",
            "named-conditional-group-exists-no-else-alternation-module-search-second-arm-str",
            "named-conditional-group-exists-no-else-alternation-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-empty-else-alternation-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-else-alternation-compile-metadata-str",
            "conditional-group-exists-empty-else-alternation-module-search-first-arm-str",
            "conditional-group-exists-empty-else-alternation-module-search-second-arm-str",
            "conditional-group-exists-empty-else-alternation-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-alternation-compile-metadata-str",
            "named-conditional-group-exists-empty-else-alternation-module-search-first-arm-str",
            "named-conditional-group-exists-empty-else-alternation-module-search-second-arm-str",
            "named-conditional-group-exists-empty-else-alternation-pattern-fullmatch-absent-str",
        ),
    },
    "conditional-group-exists-empty-yes-else-alternation-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-empty-yes-else-alternation-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-alternation-module-search-present-str",
            "conditional-group-exists-empty-yes-else-alternation-module-search-absent-first-arm-str",
            "conditional-group-exists-empty-yes-else-alternation-pattern-fullmatch-absent-second-arm-str",
            "named-conditional-group-exists-empty-yes-else-alternation-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-alternation-module-search-present-str",
            "named-conditional-group-exists-empty-yes-else-alternation-module-search-absent-first-arm-str",
            "named-conditional-group-exists-empty-yes-else-alternation-pattern-fullmatch-absent-second-arm-str",
        ),
    },
    "conditional-group-exists-fully-empty-alternation-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-fully-empty-alternation-compile-metadata-str",
            "conditional-group-exists-fully-empty-alternation-module-search-present-str",
            "conditional-group-exists-fully-empty-alternation-module-fullmatch-absent-str",
            "conditional-group-exists-fully-empty-alternation-pattern-fullmatch-extra-suffix-failure-str",
            "named-conditional-group-exists-fully-empty-alternation-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-alternation-module-search-present-str",
            "named-conditional-group-exists-fully-empty-alternation-module-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-alternation-pattern-fullmatch-extra-suffix-failure-str",
        ),
    },
    "conditional-group-exists-alternation-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-alternation-compile-metadata-str",
            "conditional-group-exists-alternation-module-search-present-first-arm-str",
            "conditional-group-exists-alternation-pattern-fullmatch-present-second-arm-str",
            "conditional-group-exists-alternation-module-search-absent-first-arm-str",
            "conditional-group-exists-alternation-pattern-fullmatch-absent-second-arm-str",
            "named-conditional-group-exists-alternation-compile-metadata-str",
            "named-conditional-group-exists-alternation-module-search-present-first-arm-str",
            "named-conditional-group-exists-alternation-pattern-fullmatch-present-second-arm-str",
            "named-conditional-group-exists-alternation-module-search-absent-first-arm-str",
            "named-conditional-group-exists-alternation-pattern-fullmatch-absent-second-arm-str",
        ),
    },
    "conditional-group-exists-quantified-alternation-workflows": {
        "representative_case_ids": (
            "conditional-group-exists-quantified-alternation-compile-metadata-str",
            "conditional-group-exists-quantified-alternation-module-search-present-first-arm-str",
            "conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
            "conditional-group-exists-quantified-alternation-module-search-absent-first-arm-str",
            "conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
            "named-conditional-group-exists-quantified-alternation-compile-metadata-str",
            "named-conditional-group-exists-quantified-alternation-module-search-present-first-arm-str",
            "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
            "named-conditional-group-exists-quantified-alternation-module-search-absent-first-arm-str",
            "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
        ),
    },
}


QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "quantified-alternation-broader-range-workflows": {
        "representative_case_ids": (
            "quantified-alternation-broader-range-numbered-compile-metadata-str",
            "quantified-alternation-broader-range-numbered-module-search-lower-bound-b-str",
            "quantified-alternation-broader-range-numbered-module-search-lower-bound-c-str",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bbb-str",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcc-str",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcb-str",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-overflow-str",
            "quantified-alternation-broader-range-named-compile-metadata-str",
            "quantified-alternation-broader-range-named-module-search-lower-bound-b-str",
            "quantified-alternation-broader-range-named-module-search-lower-bound-c-str",
            "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bbb-str",
            "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcc-str",
            "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcb-str",
            "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-below-lower-bound-str",
            "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-overflow-str",
        ),
    },
    "quantified-alternation-open-ended-workflows": {
        "representative_case_ids": (
            "quantified-alternation-open-ended-numbered-compile-metadata-str",
            "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-str",
            "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-str",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-str",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-str",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-str",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-str",
            "quantified-alternation-open-ended-named-compile-metadata-str",
            "quantified-alternation-open-ended-named-module-search-lower-bound-b-str",
            "quantified-alternation-open-ended-named-module-search-lower-bound-c-str",
            "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-str",
            "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-str",
            "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-str",
            "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-str",
            "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-str",
        ),
    },
    "quantified-alternation-nested-branch-workflows": {
        "representative_case_ids": (
            "quantified-alternation-nested-branch-numbered-compile-metadata-str",
            "quantified-alternation-nested-branch-numbered-module-search-lower-bound-inner-branch-str",
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-lower-bound-literal-branch-str",
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-second-repetition-mixed-branches-str",
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-no-match-str",
            "quantified-alternation-nested-branch-named-compile-metadata-str",
            "quantified-alternation-nested-branch-named-module-search-lower-bound-literal-branch-str",
            "quantified-alternation-nested-branch-named-pattern-fullmatch-lower-bound-inner-branch-str",
            "quantified-alternation-nested-branch-named-pattern-fullmatch-second-repetition-mixed-branches-str",
            "quantified-alternation-nested-branch-named-pattern-fullmatch-no-match-str",
        ),
    },
    "quantified-alternation-backtracking-heavy-workflows": {
        "representative_case_ids": (
            "quantified-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "quantified-alternation-backtracking-heavy-numbered-module-search-lower-bound-b-branch-str",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-bc-branch-str",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-b-then-bc-str",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-b-str",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-bc-str",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-str",
            "quantified-alternation-backtracking-heavy-named-compile-metadata-str",
            "quantified-alternation-backtracking-heavy-named-module-search-lower-bound-bc-branch-str",
            "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-b-then-b-str",
            "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-bc-then-b-str",
            "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-str",
        ),
    },
    "quantified-alternation-conditional-workflows": {
        "representative_case_ids": (
            "quantified-alternation-conditional-numbered-compile-metadata-str",
            "quantified-alternation-conditional-numbered-module-search-absent-workflow-str",
            "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-str",
            "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-str",
            "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str",
            "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-str",
            "quantified-alternation-conditional-named-compile-metadata-str",
            "quantified-alternation-conditional-named-module-search-absent-workflow-str",
            "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-str",
            "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-str",
            "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-str",
            "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-str",
        ),
    },
    "quantified-alternation-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "quantified-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
            "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
            "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
            "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
            "quantified-alternation-branch-local-named-backreference-compile-metadata-str",
            "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
            "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-str",
            "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
            "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
        ),
    },
}


CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-replacement-present-str",
            "module-subn-conditional-group-exists-replacement-absent-str",
            "pattern-sub-conditional-group-exists-replacement-present-str",
            "pattern-subn-conditional-group-exists-replacement-absent-str",
            "module-sub-named-conditional-group-exists-replacement-present-str",
            "module-subn-named-conditional-group-exists-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-replacement-absent-str",
        ),
    },
    "conditional-group-exists-no-else-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-no-else-replacement-present-str",
            "module-subn-conditional-group-exists-no-else-replacement-absent-str",
            "pattern-sub-conditional-group-exists-no-else-replacement-present-str",
            "pattern-subn-conditional-group-exists-no-else-replacement-absent-str",
            "module-sub-named-conditional-group-exists-no-else-replacement-present-str",
            "module-subn-named-conditional-group-exists-no-else-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-no-else-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-no-else-replacement-absent-str",
        ),
    },
    "conditional-group-exists-empty-else-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-empty-else-replacement-present-str",
            "module-subn-conditional-group-exists-empty-else-replacement-absent-str",
            "pattern-sub-conditional-group-exists-empty-else-replacement-present-str",
            "pattern-subn-conditional-group-exists-empty-else-replacement-absent-str",
            "module-sub-named-conditional-group-exists-empty-else-replacement-present-str",
            "module-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-empty-else-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
        ),
    },
    "conditional-group-exists-empty-yes-else-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
            "module-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
            "pattern-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
            "pattern-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
            "module-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
            "module-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
        ),
    },
    "conditional-group-exists-fully-empty-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-fully-empty-replacement-present-str",
            "module-subn-conditional-group-exists-fully-empty-replacement-absent-str",
            "pattern-sub-conditional-group-exists-fully-empty-replacement-present-str",
            "pattern-subn-conditional-group-exists-fully-empty-replacement-absent-str",
            "module-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
            "module-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
        ),
    },
    "conditional-group-exists-alternation-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-alternation-replacement-present-first-arm-str",
            "module-subn-conditional-group-exists-alternation-replacement-present-second-arm-str",
            "pattern-sub-conditional-group-exists-alternation-replacement-absent-first-arm-str",
            "pattern-subn-conditional-group-exists-alternation-replacement-absent-second-arm-str",
            "module-sub-named-conditional-group-exists-alternation-replacement-present-first-arm-str",
            "module-subn-named-conditional-group-exists-alternation-replacement-present-second-arm-str",
            "pattern-sub-named-conditional-group-exists-alternation-replacement-absent-first-arm-str",
            "pattern-subn-named-conditional-group-exists-alternation-replacement-absent-second-arm-str",
        ),
    },
    "conditional-group-exists-nested-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-nested-replacement-present-str",
            "module-subn-conditional-group-exists-nested-replacement-absent-str",
            "pattern-sub-conditional-group-exists-nested-replacement-present-str",
            "pattern-subn-conditional-group-exists-nested-replacement-absent-str",
            "module-sub-named-conditional-group-exists-nested-replacement-present-str",
            "module-subn-named-conditional-group-exists-nested-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-nested-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-nested-replacement-absent-str",
        ),
    },
    "conditional-group-exists-quantified-replacement-workflows": {
        "representative_case_ids": (
            "module-sub-conditional-group-exists-quantified-replacement-present-str",
            "module-subn-conditional-group-exists-quantified-replacement-absent-str",
            "pattern-sub-conditional-group-exists-quantified-replacement-present-str",
            "pattern-subn-conditional-group-exists-quantified-replacement-absent-str",
            "module-sub-named-conditional-group-exists-quantified-replacement-present-str",
            "module-subn-named-conditional-group-exists-quantified-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-quantified-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-quantified-replacement-absent-str",
        ),
    },
}


WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS = {
    "wider-ranged-repeat-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "wider-ranged-repeat-quantified-group-alternation-numbered-compile-metadata-str",
            "wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
            "wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
            "wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-mixed-str",
            "wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
            "wider-ranged-repeat-quantified-group-alternation-named-compile-metadata-str",
            "wider-ranged-repeat-quantified-group-alternation-named-module-search-mixed-str",
            "wider-ranged-repeat-quantified-group-alternation-named-module-search-upper-bound-mixed-str",
            "wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-upper-bound-de-str",
            "wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-overflow-str",
        ),
    },
    "wider-ranged-repeat-quantified-group-alternation-conditional-workflows": {
        "representative_case_ids": (
            "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-mixed-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-mixed-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-mixed-workflow-str",
            "wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
        ),
    },
    "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows": {
        "representative_case_ids": (
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-long-branch-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-short-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-overlap-tail-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-third-repetition-short-short-long-str",
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-str",
        ),
    },
    "broader-range-wider-ranged-repeat-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-compile-metadata-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-named-compile-metadata-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-mixed-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-upper-bound-all-de-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-upper-bound-mixed-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-overflow-str",
        ),
    },
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows": {
        "representative_case_ids": (
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-str",
        ),
    },
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows": {
        "representative_case_ids": (
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-short-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-mixed-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-overflow-workflow-str",
        ),
    },
    "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows": {
        "representative_case_ids": (
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-mixed-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-short-then-long-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-mixed-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-invalid-tail-str",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-overflow-str",
        ),
    },
}


NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS = {
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-upper-bound-all-de-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-missing-trailing-d-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-lower-bound-bc-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-lower-bound-de-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-upper-bound-all-de-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-short-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-overflow-str",
        ),
    },
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows": {
        "representative_case_ids": (
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-mixed-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-e-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-short-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-all-de-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-mixed-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-overflow-workflow-str",
        ),
    },
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows": {
        "representative_case_ids": (
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-mixed-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-short-then-long-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-mixed-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-invalid-tail-str",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-overflow-str",
        ),
    },
}


OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS = {
    "open-ended-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "open-ended-quantified-group-alternation-numbered-compile-metadata-str",
            "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
            "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-second-repetition-bc-bc-str",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-second-repetition-bc-de-str",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-invalid-branch-str",
            "open-ended-quantified-group-alternation-named-compile-metadata-str",
            "open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-str",
            "open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-second-repetition-bc-de-str",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-str",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-below-lower-bound-str",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-invalid-branch-str",
        ),
    },
    "nested-open-ended-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "nested-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
            "nested-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
            "nested-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-fourth-repetition-de-str",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-missing-trailing-d-str",
            "nested-open-ended-quantified-group-alternation-named-compile-metadata-str",
            "nested-open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-str",
            "nested-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-str",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-short-str",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-missing-trailing-d-str",
        ),
    },
    "broader-range-open-ended-quantified-group-alternation-workflows": {
        "representative_case_ids": (
            "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-second-repetition-bc-de-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-fourth-repetition-de-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-one-repetition-str",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-zero-repetition-str",
            "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",
            "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-str",
            "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-second-repetition-bc-de-str",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-str",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-one-repetition-str",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-zero-repetition-str",
        ),
    },
    "open-ended-quantified-group-alternation-conditional-workflows": {
        "representative_case_ids": (
            "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
            "open-ended-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
            "open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
            "open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
            "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str",
            "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
            "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str",
            "open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
            "open-ended-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
            "open-ended-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
            "open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
            "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
            "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
        ),
    },
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows": {
        "representative_case_ids": (
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-one-repetition-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
        ),
    },
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows": {
        "representative_case_ids": (
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-long-branch-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-short-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-overlap-tail-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-str",
        ),
    },
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows": {
        "representative_case_ids": (
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-short-only-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-one-repetition-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-short-only-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-short-then-long-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-one-repetition-str",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-str",
        ),
    },
}


@dataclass(frozen=True)
class CorrectnessLayerExpectation:
    layer_id: str
    expected_manifest_ids: tuple[str, ...]
    expected_operations: tuple[str, ...]
    expected_text_models: tuple[str, ...]


@dataclass(frozen=True)
class CorrectnessScorecardExpectation:
    fixture_paths: tuple[pathlib.Path, ...]
    expected_fixture_case_count: int
    expected_fixture_manifest_ids: tuple[str, ...]
    expected_fixture_paths: tuple[str, ...]
    expected_phase: str
    expected_cumulative_suite_ids: tuple[str, ...]
    expected_suite_ids: tuple[str, ...]
    layer_expectations: tuple[CorrectnessLayerExpectation, ...]
    representative_cases: tuple[FixtureCase, ...]
    target_layer_id: str
    target_layer_manifest_ids: tuple[str, ...]
    target_layer_operations: tuple[str, ...]
    target_layer_text_models: tuple[str, ...]
    target_manifest_case_count: int
    target_manifest_id: str
    target_suite_families: tuple[str, ...]
    target_suite_id: str
    target_suite_operations: tuple[str, ...]
    target_suite_text_models: tuple[str, ...]


def _sorted_unique_strings(values: object) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values if value is not None}))


@lru_cache(maxsize=1)
def _fixture_inventory() -> tuple[tuple[pathlib.Path, FixtureManifest, tuple[FixtureCase, ...]], ...]:
    inventory = []
    for path in DEFAULT_FIXTURE_PATHS:
        manifest, cases = load_fixture_manifest(path)
        inventory.append((path, manifest, tuple(cases)))
    return tuple(inventory)


def _expected_target_manifest_ids(
    expectations: dict[str, dict[str, tuple[str, ...]]],
    *,
    expectation_label: str,
) -> tuple[str, ...]:
    target_manifest_ids = tuple(
        manifest.manifest_id
        for _, manifest, _ in _fixture_inventory()
        if manifest.manifest_id in expectations
    )
    missing_expectations = set(expectations) - set(target_manifest_ids)
    if missing_expectations:
        raise AssertionError(
            f"{expectation_label} manifest expectations drifted from DEFAULT_FIXTURE_PATHS: "
            f"missing {sorted(missing_expectations)}"
        )
    return target_manifest_ids


def _build_scorecard_expectation(
    target_manifest_id: str,
    expectation_table: dict[str, dict[str, tuple[str, ...]]],
) -> CorrectnessScorecardExpectation:
    selected_paths: list[pathlib.Path] = []
    selected_manifests: list[FixtureManifest] = []
    selected_cases: list[FixtureCase] = []
    target_cases: tuple[FixtureCase, ...] | None = None
    target_manifest: FixtureManifest | None = None

    for path, manifest, cases in _fixture_inventory():
        selected_paths.append(path)
        selected_manifests.append(manifest)
        selected_cases.extend(cases)
        if manifest.manifest_id == target_manifest_id:
            target_manifest = manifest
            target_cases = cases
            break

    if target_manifest is None or target_cases is None:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in DEFAULT_FIXTURE_PATHS"
        )

    expectation = expectation_table.get(target_manifest_id)
    if expectation is None:
        raise AssertionError(f"missing correctness expectation for {target_manifest_id!r}")

    representative_case_ids = expectation["representative_case_ids"]
    target_cases_by_id = {case.case_id: case for case in target_cases}
    missing_case_ids = sorted(
        case_id for case_id in representative_case_ids if case_id not in target_cases_by_id
    )
    if missing_case_ids:
        raise AssertionError(
            f"missing representative cases for {target_manifest_id!r}: {missing_case_ids}"
        )

    selected_cases_by_manifest_id = {
        manifest.manifest_id: tuple(
            case for case in selected_cases if case.manifest_id == manifest.manifest_id
        )
        for manifest in selected_manifests
    }
    target_suite_cases = tuple(
        case for case in target_cases if case.suite_id == target_manifest.suite_id
    )
    target_suite_operations = _sorted_unique_strings(
        case.operation for case in target_suite_cases
    )
    target_suite_text_models = _sorted_unique_strings(
        case.text_model for case in target_suite_cases
    )
    expected_suite_ids = [target_manifest.suite_id]
    expected_suite_ids.extend(
        f"{target_manifest.suite_id}.{text_model}"
        for text_model in target_suite_text_models
    )
    if len(target_suite_operations) > 1:
        expected_suite_ids.extend(
            f"{target_manifest.suite_id}.{operation}"
            for operation in target_suite_operations
        )

    expected_cumulative_suite_ids: list[str] = []
    for manifest in selected_manifests:
        manifest_cases = selected_cases_by_manifest_id[manifest.manifest_id]
        expected_cumulative_suite_ids.append(manifest.suite_id)
        expected_cumulative_suite_ids.extend(
            f"{manifest.suite_id}.{text_model}"
            for text_model in _sorted_unique_strings(
                case.text_model for case in manifest_cases
            )
        )
        manifest_operations = _sorted_unique_strings(
            case.operation for case in manifest_cases
        )
        if len(manifest_operations) > 1:
            expected_cumulative_suite_ids.extend(
                f"{manifest.suite_id}.{operation}" for operation in manifest_operations
            )

    target_layer_cases = [
        case for case in selected_cases if case.layer == target_manifest.layer
    ]
    layer_expectations = tuple(
        CorrectnessLayerExpectation(
            layer_id=layer_id,
            expected_manifest_ids=_sorted_unique_strings(
                case.manifest_id for case in selected_cases if case.layer == layer_id
            ),
            expected_operations=_sorted_unique_strings(
                case.operation for case in selected_cases if case.layer == layer_id
            ),
            expected_text_models=_sorted_unique_strings(
                case.text_model for case in selected_cases if case.layer == layer_id
            ),
        )
        for layer_id in _sorted_unique_strings(case.layer for case in selected_cases)
    )

    return CorrectnessScorecardExpectation(
        fixture_paths=tuple(selected_paths),
        expected_fixture_case_count=len(selected_cases),
        expected_fixture_manifest_ids=tuple(
            manifest.manifest_id for manifest in selected_manifests
        ),
        expected_fixture_paths=tuple(
            str(path.relative_to(REPO_ROOT)) for path in selected_paths
        ),
        expected_phase=determine_phase(
            {manifest.layer: {} for manifest in selected_manifests}
        ),
        expected_cumulative_suite_ids=tuple(expected_cumulative_suite_ids),
        expected_suite_ids=tuple(expected_suite_ids),
        layer_expectations=layer_expectations,
        representative_cases=tuple(
            target_cases_by_id[case_id] for case_id in representative_case_ids
        ),
        target_layer_id=target_manifest.layer,
        target_layer_manifest_ids=_sorted_unique_strings(
            manifest.manifest_id
            for manifest in selected_manifests
            if manifest.layer == target_manifest.layer
        ),
        target_layer_operations=_sorted_unique_strings(
            case.operation for case in target_layer_cases
        ),
        target_layer_text_models=_sorted_unique_strings(
            case.text_model for case in target_layer_cases
        ),
        target_manifest_case_count=len(target_cases),
        target_manifest_id=target_manifest.manifest_id,
        target_suite_families=_sorted_unique_strings(
            case.family for case in target_suite_cases
        ),
        target_suite_id=target_manifest.suite_id,
        target_suite_operations=target_suite_operations,
        target_suite_text_models=target_suite_text_models,
    )


def combined_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
        expectation_label="combined correctness",
    )


@lru_cache(maxsize=None)
def combined_correctness_case(target_manifest_id: str) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
    )


def branch_local_backreference_scorecard_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
        expectation_label="branch-local-backreference correctness scorecard",
    )


@lru_cache(maxsize=None)
def branch_local_backreference_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
    )


def conditional_nested_quantified_scorecard_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
        expectation_label="conditional nested/quantified correctness scorecard",
    )


@lru_cache(maxsize=None)
def conditional_nested_quantified_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
    )


def quantified_alternation_scorecard_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
        expectation_label="quantified-alternation correctness scorecard",
    )


@lru_cache(maxsize=None)
def quantified_alternation_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    )


def conditional_alternation_scorecard_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
        expectation_label="conditional-alternation correctness scorecard",
    )


@lru_cache(maxsize=None)
def conditional_alternation_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    )


def conditional_replacement_scorecard_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
        expectation_label="conditional replacement correctness scorecard",
    )


@lru_cache(maxsize=None)
def conditional_replacement_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
    )


def wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids(
) -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
        expectation_label="wider-ranged-repeat quantified-group scorecard",
    )


@lru_cache(maxsize=None)
def wider_ranged_repeat_quantified_group_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    )


def nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids(
) -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS,
        expectation_label=(
            "nested broader-range wider-ranged-repeat quantified-group "
            "alternation scorecard"
        ),
    )


@lru_cache(maxsize=None)
def nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS,
    )


def open_ended_quantified_group_scorecard_target_manifest_ids() -> tuple[str, ...]:
    return _expected_target_manifest_ids(
        OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
        expectation_label="open-ended quantified-group scorecard",
    )


@lru_cache(maxsize=None)
def open_ended_quantified_group_scorecard_case(
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    return _build_scorecard_expectation(
        target_manifest_id,
        OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    )
