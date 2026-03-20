from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import lru_cache, partial
import pathlib
import re
import subprocess
from typing import Any
import unittest
import warnings

from rebar_harness import correctness
from rebar_harness.scorecard_io import build_cpython_baseline
from tests.conftest import REPO_ROOT, run_harness_scorecard

from rebar_harness.correctness import (
    CpythonReAdapter,
    FixtureCase,
    FixtureManifest,
    RebarAdapter,
    determine_phase,
    evaluate_case,
    load_fixture_manifest,
    published_fixture_manifests,
)

TRACKED_REPORT_PATH = correctness.SCORECARD_REPORT.published_path

@dataclass(frozen=True)
class CorrectnessScorecardManifestExpectation:
    representative_case_ids: tuple[str, ...]
    tracked_report_freshness_sample: bool = False


COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS = {
    "parser-matrix": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "str-literal-success",
            "str-inline-unicode-flag-success",
            "str-character-class-ignorecase-success",
            "str-possessive-quantifier-success",
            "str-atomic-group-success",
            "str-fixed-width-lookbehind-success",
            "str-parser-stress-compile-proxy-success",
            "str-nested-set-warning",
            "str-variable-width-lookbehind-error",
            "bytes-inline-unicode-flag-error",
            "bytes-inline-locale-flag-success",
            "bytes-named-backreference-compile-proxy-success",
        ),
    ),
    "public-api-surface": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "compile-pattern-scaffold-success",
            "purge-noop-success",
            "search-literal-success",
            "escape-success",
        ),
    ),
    "match-behavior-smoke": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "search-str-success-literal",
            "match-str-no-match",
            "fullmatch-bytes-success-literal",
        ),
    ),
    "exported-symbol-surface": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "regexflag-type-metadata",
            "error-type-metadata",
            "ascii-constant-value",
            "pattern-type-metadata",
            "pattern-constructor-guard",
        ),
    ),
    "pattern-object-surface": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "pattern-object-str-metadata",
            "pattern-object-bytes-ignorecase-metadata",
            "pattern-search-literal-success",
        ),
    ),
    "module-workflow-surface": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "workflow-compile-str-anchored-literal",
            "workflow-compile-str-bounded-wildcard",
            "workflow-compile-str-bounded-wildcard-ignorecase",
            "workflow-pattern-search-str-bounded-wildcard-ignorecase",
            "workflow-pattern-match-str-bounded-wildcard",
            "workflow-pattern-fullmatch-str-bounded-wildcard",
            "workflow-pattern-findall-str-bounded-wildcard",
            "workflow-pattern-finditer-str-bounded-wildcard",
            "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
            "workflow-compile-str-verbose-regression",
            "workflow-compile-str-multiline-regression",
            "workflow-compile-bytes-verbose-regression",
            "workflow-compile-bytes-multiline-regression",
            "workflow-pattern-search-str-verbose-regression",
            "workflow-pattern-search-str-verbose-regression-digits",
            "workflow-pattern-search-str-verbose-regression-too-many-digits",
            "workflow-pattern-search-bytes-verbose-regression",
            "workflow-pattern-search-bytes-verbose-regression-digits",
            "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
            "workflow-pattern-fullmatch-str-verbose-regression",
            "workflow-pattern-fullmatch-str-verbose-regression-alpha",
            "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
            "workflow-pattern-fullmatch-bytes-verbose-regression",
            "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
            "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
            "workflow-pattern-search-str-pos-keyword",
            "workflow-pattern-match-str-pos-keyword",
            "workflow-pattern-fullmatch-bytes-window-keyword",
            "workflow-pattern-findall-str-window-keyword",
            "workflow-pattern-finditer-bytes-window-keyword",
            "workflow-module-search-str-bounded-wildcard-ignorecase",
            "workflow-module-match-str-bounded-wildcard-miss",
            "workflow-module-fullmatch-str-bounded-wildcard",
            "workflow-module-search-flags-keyword-str",
            "workflow-module-match-flags-keyword-bytes",
            "workflow-module-fullmatch-flags-keyword-str",
            "workflow-module-split-maxsplit-keyword-bytes",
            "workflow-module-sub-count-keyword-str",
            "workflow-module-sub-count-indexlike-str",
            "workflow-module-subn-count-keyword-bytes",
            "workflow-module-subn-count-indexlike-bytes",
            "workflow-module-search-str-compiled-pattern",
            "workflow-module-match-str-compiled-pattern",
            "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
            "workflow-module-match-str-bounded-wildcard-compiled-pattern",
            "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
            "workflow-module-search-bytes-verbose-regression-compiled-pattern",
            "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
            "workflow-module-split-str-compiled-pattern",
            "workflow-module-findall-bytes-compiled-pattern",
            "workflow-module-finditer-str-compiled-pattern",
            "workflow-module-sub-str-compiled-pattern",
            "workflow-module-sub-str-compiled-pattern-on-bytes-string",
            "workflow-module-subn-bytes-compiled-pattern",
            "workflow-module-subn-bytes-compiled-pattern-on-str-string",
            "workflow-cache-hit-str",
            "workflow-purge-reset-str",
            "workflow-pattern-search-str",
            "workflow-pattern-fullmatch-bytes",
            "workflow-escape-bytes",
        ),
    ),
    "collection-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-finditer-str-repeated",
            "pattern-split-bytes-maxsplit",
            "module-subn-bytes-count",
            "module-sub-template-str",
            "module-sub-callable-str",
            "module-sub-grouping-template",
            "module-findall-nonliteral-str",
        ),
    ),
    "literal-flag-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "flag-module-search-ignorecase-str-hit",
            "flag-module-search-ignorecase-ascii-str-hit",
            "flag-pattern-search-ignorecase-ascii-str-hit",
            "flag-pattern-fullmatch-ignorecase-str-miss",
            "flag-pattern-match-ignorecase-bytes-hit",
            "flag-cache-distinct-str-normalized",
            "flag-unsupported-inline-flag-search",
            "flag-unsupported-locale-bytes-search",
            "flag-unsupported-nonliteral-ignorecase-search",
        ),
    ),
    "grouped-match-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "grouped-module-search-single-capture-str",
            "grouped-pattern-match-single-capture-str",
            "grouped-module-fullmatch-two-capture-gap-str",
        ),
    ),
    "named-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "named-group-compile-metadata-str",
            "named-group-module-search-metadata-str",
            "named-group-pattern-search-metadata-str",
        ),
    ),
    "named-group-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-named-group-str",
            "module-subn-template-named-group-str",
            "pattern-sub-template-named-group-str",
            "pattern-subn-template-named-group-str",
        ),
    ),
    "named-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "named-backreference-compile-metadata-str",
            "named-backreference-module-search-str",
            "named-backreference-pattern-search-str",
        ),
    ),
    "numbered-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "numbered-backreference-compile-metadata-str",
            "numbered-backreference-module-search-str",
            "numbered-backreference-pattern-search-str",
            "numbered-backreference-segment-module-search-str",
            "numbered-backreference-prefix-pattern-search-str",
        ),
        tracked_report_freshness_sample=True,
    ),
    "grouped-segment-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "grouped-segment-compile-metadata-str",
            "named-grouped-segment-compile-metadata-str",
            "grouped-segment-module-search-str",
            "grouped-segment-leading-capture-module-search-str",
            "grouped-segment-leading-capture-pattern-search-str",
            "named-grouped-segment-pattern-fullmatch-str",
        ),
    ),
    "nested-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-group-compile-metadata-str",
            "named-nested-group-compile-metadata-str",
            "nested-group-module-search-str",
            "named-nested-group-pattern-fullmatch-str",
        ),
    ),
    "literal-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "literal-alternation-compile-metadata-str",
            "literal-alternation-module-search-str",
            "literal-alternation-pattern-fullmatch-str",
        ),
    ),
    "grouped-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "grouped-alternation-compile-metadata-str",
            "named-grouped-alternation-compile-metadata-str",
            "grouped-alternation-module-search-str",
            "named-grouped-alternation-pattern-fullmatch-str",
        ),
    ),
    "grouped-alternation-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-grouped-alternation-str",
            "module-subn-template-grouped-alternation-str",
            "pattern-sub-template-named-grouped-alternation-str",
            "pattern-subn-template-named-grouped-alternation-str",
        ),
    ),
    "grouped-alternation-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-grouped-alternation-str",
            "module-subn-callable-grouped-alternation-str",
            "pattern-sub-callable-named-grouped-alternation-str",
        ),
    ),
    "branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "branch-local-numbered-backreference-compile-metadata-str",
            "branch-local-numbered-backreference-module-search-str",
            "branch-local-numbered-backreference-pattern-fullmatch-str",
            "branch-local-named-backreference-compile-metadata-str",
            "branch-local-named-backreference-module-search-str",
            "branch-local-named-backreference-pattern-fullmatch-str",
        ),
    ),
    "optional-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "optional-group-compile-metadata-str",
            "optional-group-module-search-present-str",
            "optional-group-pattern-fullmatch-absent-str",
            "named-optional-group-compile-metadata-str",
            "named-optional-group-module-search-absent-str",
            "named-optional-group-pattern-fullmatch-present-str",
            "systematic-optional-group-numbered-pattern-fullmatch-present-str",
            "systematic-optional-group-named-module-search-present-str",
        ),
    ),
    "exact-repeat-quantified-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "exact-repeat-numbered-group-compile-metadata-str",
            "exact-repeat-numbered-group-module-search-str",
            "exact-repeat-numbered-group-pattern-fullmatch-str",
            "exact-repeat-named-group-compile-metadata-str",
            "exact-repeat-named-group-module-search-str",
            "exact-repeat-named-group-pattern-fullmatch-str",
        ),
    ),
    "exact-repeat-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "ranged-repeat-quantified-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "ranged-repeat-numbered-group-compile-metadata-str",
            "ranged-repeat-numbered-group-module-search-lower-bound-str",
            "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
            "ranged-repeat-named-group-compile-metadata-str",
            "ranged-repeat-named-group-module-search-upper-bound-str",
            "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
        ),
    ),
    "wider-ranged-repeat-quantified-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "wider-ranged-repeat-numbered-group-compile-metadata-str",
            "wider-ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
            "wider-ranged-repeat-named-group-module-search-upper-bound-str",
            "wider-ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
        ),
    ),
    "broader-range-wider-ranged-repeat-quantified-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "broader-range-wider-ranged-repeat-numbered-group-compile-metadata-str",
            "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
            "broader-range-wider-ranged-repeat-numbered-group-pattern-fullmatch-lower-bound-str",
            "broader-range-wider-ranged-repeat-named-group-compile-metadata-str",
            "broader-range-wider-ranged-repeat-named-group-module-search-upper-bound-str",
            "broader-range-wider-ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
        ),
    ),
    "nested-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-group-alternation-compile-metadata-str",
            "named-nested-group-alternation-pattern-fullmatch-str",
        ),
    ),
    "nested-group-alternation-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-group-alternation-numbered-outer-str",
            "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
            "module-sub-template-nested-group-alternation-numbered-wrapper-str",
            "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
        ),
    ),
    "nested-group-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-group-numbered-str",
            "module-subn-template-nested-group-numbered-str",
            "pattern-sub-template-nested-group-named-str",
            "pattern-subn-template-nested-group-named-str",
        ),
    ),
    "quantified-nested-group-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
            "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
            "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
            "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
        ),
    ),
    "quantified-nested-group-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
            "module-subn-callable-quantified-nested-group-numbered-first-match-only-str",
            "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str",
            "pattern-subn-callable-quantified-nested-group-named-first-match-only-str",
        ),
    ),
    "nested-group-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-group-numbered-str",
            "module-subn-callable-nested-group-numbered-str",
            "pattern-sub-callable-nested-group-named-str",
        ),
    ),
    "nested-group-alternation-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-group-alternation-numbered-b-branch-str",
            "pattern-sub-callable-nested-group-alternation-numbered-mixed-branches-str",
            "module-sub-callable-nested-group-alternation-named-c-branch-str",
            "pattern-subn-callable-nested-group-alternation-named-b-branch-first-match-only-str",
        ),
    ),
    "nested-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-group-alternation-branch-local-backreference-numbered-b-branch-str",
            "module-subn-callable-nested-group-alternation-branch-local-backreference-numbered-first-match-only-str",
            "module-sub-callable-nested-group-alternation-branch-local-backreference-named-c-branch-str",
            "pattern-subn-callable-nested-group-alternation-branch-local-backreference-named-b-branch-first-match-only-str",
        ),
    ),
    "quantified-nested-group-alternation-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-quantified-nested-group-alternation-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-quantified-nested-group-alternation-numbered-mixed-branches-str",
            "module-sub-callable-quantified-nested-group-alternation-named-lower-bound-c-branch-str",
            "pattern-subn-callable-quantified-nested-group-alternation-named-first-match-only-c-branch-str",
        ),
    ),
    "optional-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "optional-group-alternation-compile-metadata-str",
            "optional-group-alternation-module-search-present-str",
            "optional-group-alternation-pattern-fullmatch-absent-str",
            "named-optional-group-alternation-compile-metadata-str",
            "named-optional-group-alternation-module-search-present-str",
            "named-optional-group-alternation-pattern-fullmatch-absent-str",
        ),
    ),
    "optional-group-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "optional-group-conditional-compile-metadata-str",
            "optional-group-conditional-module-search-present-str",
            "optional-group-conditional-pattern-fullmatch-absent-str",
            "named-optional-group-conditional-compile-metadata-str",
            "named-optional-group-conditional-module-search-present-str",
            "named-optional-group-conditional-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-compile-metadata-str",
            "conditional-group-exists-module-search-present-str",
            "conditional-group-exists-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-compile-metadata-str",
            "named-conditional-group-exists-module-search-present-str",
            "named-conditional-group-exists-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-no-else-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-no-else-compile-metadata-str",
            "conditional-group-exists-no-else-module-search-present-str",
            "conditional-group-exists-no-else-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-compile-metadata-str",
            "named-conditional-group-exists-no-else-module-search-present-str",
            "named-conditional-group-exists-no-else-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-empty-else-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-else-compile-metadata-str",
            "conditional-group-exists-empty-else-module-search-present-str",
            "conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-compile-metadata-str",
            "named-conditional-group-exists-empty-else-module-search-present-str",
            "named-conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-empty-yes-else-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-yes-else-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-module-search-present-str",
            "conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-yes-else-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-module-search-present-str",
            "named-conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-fully-empty-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-fully-empty-compile-metadata-str",
            "conditional-group-exists-fully-empty-module-search-present-str",
            "conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-module-search-present-str",
            "named-conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-assertion-diagnostics": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-assertion-positive-lookahead-error-str",
            "conditional-group-exists-assertion-negative-lookahead-error-str",
        ),
    ),
    "quantified-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "quantified-alternation-numbered-compile-metadata-str",
            "quantified-alternation-numbered-module-search-lower-bound-str",
            "quantified-alternation-numbered-pattern-fullmatch-second-repetition-str",
            "quantified-alternation-named-compile-metadata-str",
            "quantified-alternation-named-module-search-second-repetition-str",
            "quantified-alternation-named-pattern-fullmatch-lower-bound-str",
            "quantified-alternation-numbered-compile-metadata-bytes",
            "quantified-alternation-numbered-module-search-lower-bound-bytes",
            "quantified-alternation-numbered-pattern-fullmatch-second-repetition-bytes",
            "quantified-alternation-named-compile-metadata-bytes",
            "quantified-alternation-named-module-search-second-repetition-bytes",
            "quantified-alternation-named-pattern-fullmatch-lower-bound-bytes",
        ),
    ),
    "quantified-nested-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "quantified-nested-group-alternation-numbered-compile-metadata-str",
            "quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str",
            "quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str",
            "quantified-nested-group-alternation-named-compile-metadata-str",
            "quantified-nested-group-alternation-named-module-search-lower-bound-c-str",
            "quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str",
        ),
    ),
    "nested-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
            "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
            "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
            "nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
            "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
            "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
        ),
    ),
    "quantified-nested-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-bytes",
            "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-bytes",
            "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
            "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
            "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
            "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-bytes",
            "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-bytes",
        ),
        tracked_report_freshness_sample=True,
    ),
    "quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-quantified-nested-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-quantified-nested-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-callable-quantified-nested-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
            "pattern-subn-callable-quantified-nested-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
        ),
        tracked_report_freshness_sample=True,
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "pattern-subn-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
        ),
    ),
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-bytes",
        ),
        tracked_report_freshness_sample=True,
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-bytes",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
        tracked_report_freshness_sample=True,
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
        ),
    ),
    "conditional-group-exists-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-conditional-group-exists-present-str",
            "pattern-subn-callable-conditional-group-exists-absent-str",
            "module-sub-callable-named-conditional-group-exists-present-str",
            "pattern-subn-callable-named-conditional-group-exists-absent-str",
        ),
    ),
    "conditional-group-exists-replacement-template-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-conditional-group-exists-replacement-present-str",
            "pattern-subn-template-conditional-group-exists-replacement-absent-str",
            "module-sub-template-named-conditional-group-exists-replacement-present-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-absent-str",
        ),
    ),
}


BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-branch-local-numbered-backreference-compile-metadata-str",
            "conditional-group-exists-branch-local-numbered-backreference-module-search-present-str",
            "conditional-group-exists-branch-local-numbered-backreference-pattern-fullmatch-absent-str",
            "conditional-group-exists-branch-local-named-backreference-compile-metadata-str",
            "conditional-group-exists-branch-local-named-backreference-module-search-present-str",
            "conditional-group-exists-branch-local-named-backreference-pattern-fullmatch-absent-str",
        ),
    ),
    "optional-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "quantified-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "quantified-branch-local-numbered-backreference-compile-metadata-str",
            "quantified-branch-local-numbered-backreference-module-search-lower-bound-str",
            "quantified-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-str",
            "quantified-branch-local-numbered-backreference-pattern-fullmatch-absent-branch-str",
            "quantified-branch-local-named-backreference-compile-metadata-str",
            "quantified-branch-local-named-backreference-module-search-lower-bound-str",
            "quantified-branch-local-named-backreference-pattern-fullmatch-second-iteration-str",
            "quantified-branch-local-named-backreference-pattern-fullmatch-absent-branch-str",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-bytes",
        ),
    ),
}


CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-nested-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-nested-compile-metadata-str",
            "conditional-group-exists-nested-module-search-present-str",
            "conditional-group-exists-nested-module-fullmatch-absent-str",
            "conditional-group-exists-nested-pattern-fullmatch-unreachable-inner-else-str",
            "named-conditional-group-exists-nested-compile-metadata-str",
            "named-conditional-group-exists-nested-module-search-present-str",
            "named-conditional-group-exists-nested-module-fullmatch-absent-str",
            "named-conditional-group-exists-nested-pattern-fullmatch-unreachable-inner-else-str",
        ),
    ),
    "conditional-group-exists-no-else-nested-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-no-else-nested-compile-metadata-str",
            "conditional-group-exists-no-else-nested-module-search-present-str",
            "conditional-group-exists-no-else-nested-module-fullmatch-missing-suffix-str",
            "conditional-group-exists-no-else-nested-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-nested-compile-metadata-str",
            "named-conditional-group-exists-no-else-nested-module-search-present-str",
            "named-conditional-group-exists-no-else-nested-module-fullmatch-missing-suffix-str",
            "named-conditional-group-exists-no-else-nested-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-quantified-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-quantified-compile-metadata-str",
            "conditional-group-exists-quantified-module-search-present-str",
            "conditional-group-exists-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
            "named-conditional-group-exists-quantified-compile-metadata-str",
            "named-conditional-group-exists-quantified-module-search-present-str",
            "named-conditional-group-exists-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
        ),
    ),
    "conditional-group-exists-no-else-quantified-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-no-else-quantified-compile-metadata-str",
            "conditional-group-exists-no-else-quantified-module-search-present-str",
            "conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
            "named-conditional-group-exists-no-else-quantified-compile-metadata-str",
            "named-conditional-group-exists-no-else-quantified-module-search-present-str",
            "named-conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
        ),
    ),
    "conditional-group-exists-empty-else-nested-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-else-nested-compile-metadata-str",
            "conditional-group-exists-empty-else-nested-module-search-present-str",
            "conditional-group-exists-empty-else-nested-module-fullmatch-missing-suffix-str",
            "conditional-group-exists-empty-else-nested-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-nested-compile-metadata-str",
            "named-conditional-group-exists-empty-else-nested-module-search-present-str",
            "named-conditional-group-exists-empty-else-nested-module-fullmatch-missing-suffix-str",
            "named-conditional-group-exists-empty-else-nested-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-empty-else-quantified-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-else-quantified-compile-metadata-str",
            "conditional-group-exists-empty-else-quantified-module-search-present-str",
            "conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
            "named-conditional-group-exists-empty-else-quantified-compile-metadata-str",
            "named-conditional-group-exists-empty-else-quantified-module-search-present-str",
            "named-conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
        ),
    ),
    "conditional-group-exists-empty-yes-else-nested-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-yes-else-nested-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-nested-module-search-present-str",
            "conditional-group-exists-empty-yes-else-nested-module-fullmatch-absent-str",
            "conditional-group-exists-empty-yes-else-nested-pattern-fullmatch-absent-failure-str",
            "named-conditional-group-exists-empty-yes-else-nested-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-nested-module-search-present-str",
            "named-conditional-group-exists-empty-yes-else-nested-module-fullmatch-absent-str",
            "named-conditional-group-exists-empty-yes-else-nested-pattern-fullmatch-absent-failure-str",
        ),
    ),
    "conditional-group-exists-empty-yes-else-quantified-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
            "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
            "conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
            "named-conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
            "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
            "named-conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
        ),
    ),
    "conditional-group-exists-fully-empty-nested-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-fully-empty-nested-compile-metadata-str",
            "conditional-group-exists-fully-empty-nested-module-search-present-str",
            "conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
            "conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
            "named-conditional-group-exists-fully-empty-nested-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-nested-module-search-present-str",
            "named-conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
        ),
    ),
    "conditional-group-exists-fully-empty-quantified-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
}


CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-no-else-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-no-else-alternation-compile-metadata-str",
            "conditional-group-exists-no-else-alternation-module-search-first-arm-str",
            "conditional-group-exists-no-else-alternation-module-search-second-arm-str",
            "conditional-group-exists-no-else-alternation-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-no-else-alternation-compile-metadata-str",
            "named-conditional-group-exists-no-else-alternation-module-search-first-arm-str",
            "named-conditional-group-exists-no-else-alternation-module-search-second-arm-str",
            "named-conditional-group-exists-no-else-alternation-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-empty-else-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-else-alternation-compile-metadata-str",
            "conditional-group-exists-empty-else-alternation-module-search-first-arm-str",
            "conditional-group-exists-empty-else-alternation-module-search-second-arm-str",
            "conditional-group-exists-empty-else-alternation-pattern-fullmatch-absent-str",
            "named-conditional-group-exists-empty-else-alternation-compile-metadata-str",
            "named-conditional-group-exists-empty-else-alternation-module-search-first-arm-str",
            "named-conditional-group-exists-empty-else-alternation-module-search-second-arm-str",
            "named-conditional-group-exists-empty-else-alternation-pattern-fullmatch-absent-str",
        ),
    ),
    "conditional-group-exists-empty-yes-else-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-empty-yes-else-alternation-compile-metadata-str",
            "conditional-group-exists-empty-yes-else-alternation-module-search-present-str",
            "conditional-group-exists-empty-yes-else-alternation-module-search-absent-first-arm-str",
            "conditional-group-exists-empty-yes-else-alternation-pattern-fullmatch-absent-second-arm-str",
            "named-conditional-group-exists-empty-yes-else-alternation-compile-metadata-str",
            "named-conditional-group-exists-empty-yes-else-alternation-module-search-present-str",
            "named-conditional-group-exists-empty-yes-else-alternation-module-search-absent-first-arm-str",
            "named-conditional-group-exists-empty-yes-else-alternation-pattern-fullmatch-absent-second-arm-str",
        ),
    ),
    "conditional-group-exists-fully-empty-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "conditional-group-exists-fully-empty-alternation-compile-metadata-str",
            "conditional-group-exists-fully-empty-alternation-module-search-present-str",
            "conditional-group-exists-fully-empty-alternation-module-fullmatch-absent-str",
            "conditional-group-exists-fully-empty-alternation-pattern-fullmatch-extra-suffix-failure-str",
            "named-conditional-group-exists-fully-empty-alternation-compile-metadata-str",
            "named-conditional-group-exists-fully-empty-alternation-module-search-present-str",
            "named-conditional-group-exists-fully-empty-alternation-module-fullmatch-absent-str",
            "named-conditional-group-exists-fully-empty-alternation-pattern-fullmatch-extra-suffix-failure-str",
        ),
    ),
    "conditional-group-exists-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "conditional-group-exists-quantified-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
}


QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "quantified-alternation-broader-range-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-alternation-broader-range-numbered-compile-metadata-bytes",
            "quantified-alternation-broader-range-numbered-module-search-lower-bound-b-bytes",
            "quantified-alternation-broader-range-numbered-module-search-lower-bound-c-bytes",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bbb-bytes",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcc-bytes",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcb-bytes",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-below-lower-bound-bytes",
            "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-overflow-bytes",
            "quantified-alternation-broader-range-named-compile-metadata-bytes",
            "quantified-alternation-broader-range-named-module-search-lower-bound-b-bytes",
            "quantified-alternation-broader-range-named-module-search-lower-bound-c-bytes",
            "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bbb-bytes",
            "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcc-bytes",
            "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcb-bytes",
            "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-below-lower-bound-bytes",
            "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-overflow-bytes",
        ),
        tracked_report_freshness_sample=True,
    ),
    "quantified-alternation-open-ended-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-alternation-open-ended-numbered-compile-metadata-bytes",
            "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-bytes",
            "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-bytes",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-bytes",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-bytes",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-bytes",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-bytes",
            "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-bytes",
            "quantified-alternation-open-ended-named-compile-metadata-bytes",
            "quantified-alternation-open-ended-named-module-search-lower-bound-b-bytes",
            "quantified-alternation-open-ended-named-module-search-lower-bound-c-bytes",
            "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-bytes",
            "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-bytes",
            "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-bytes",
            "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-bytes",
            "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-bytes",
        ),
    ),
    "quantified-alternation-nested-branch-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-alternation-nested-branch-numbered-compile-metadata-bytes",
            "quantified-alternation-nested-branch-numbered-module-search-lower-bound-inner-branch-bytes",
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-lower-bound-literal-branch-bytes",
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-second-repetition-mixed-branches-bytes",
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-no-match-bytes",
            "quantified-alternation-nested-branch-named-compile-metadata-bytes",
            "quantified-alternation-nested-branch-named-module-search-lower-bound-literal-branch-bytes",
            "quantified-alternation-nested-branch-named-pattern-fullmatch-lower-bound-inner-branch-bytes",
            "quantified-alternation-nested-branch-named-pattern-fullmatch-second-repetition-mixed-branches-bytes",
            "quantified-alternation-nested-branch-named-pattern-fullmatch-no-match-bytes",
        ),
    ),
    "quantified-alternation-backtracking-heavy-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
            "quantified-alternation-backtracking-heavy-numbered-module-search-lower-bound-b-branch-bytes",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-bc-branch-bytes",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-b-then-bc-bytes",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-b-bytes",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-bc-bytes",
            "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-bytes",
            "quantified-alternation-backtracking-heavy-named-compile-metadata-bytes",
            "quantified-alternation-backtracking-heavy-named-module-search-lower-bound-bc-branch-bytes",
            "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-b-then-b-bytes",
            "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-bc-then-b-bytes",
            "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-bytes",
        ),
    ),
    "quantified-alternation-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-alternation-conditional-numbered-compile-metadata-bytes",
            "quantified-alternation-conditional-numbered-module-search-absent-workflow-bytes",
            "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-bytes",
            "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-bytes",
            "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-bytes",
            "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-bytes",
            "quantified-alternation-conditional-named-compile-metadata-bytes",
            "quantified-alternation-conditional-named-module-search-absent-workflow-bytes",
            "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-bytes",
            "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-bytes",
            "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-bytes",
            "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-bytes",
        ),
    ),
    "quantified-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "quantified-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
            "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
            "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
            "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-bytes",
            "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-bytes",
            "quantified-alternation-branch-local-named-backreference-compile-metadata-bytes",
            "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
            "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-bytes",
            "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-bytes",
            "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-bytes",
        ),
    ),
}


CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS = {
    "conditional-group-exists-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-replacement-present-str",
            "module-subn-conditional-group-exists-replacement-absent-str",
            "pattern-sub-conditional-group-exists-replacement-present-str",
            "pattern-subn-conditional-group-exists-replacement-absent-str",
            "module-sub-named-conditional-group-exists-replacement-present-str",
            "module-subn-named-conditional-group-exists-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-replacement-template-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-conditional-group-exists-replacement-present-str",
            "module-subn-template-conditional-group-exists-replacement-absent-str",
            "pattern-sub-template-conditional-group-exists-replacement-present-str",
            "pattern-subn-template-conditional-group-exists-replacement-absent-str",
            "module-sub-template-named-conditional-group-exists-replacement-present-str",
            "module-subn-template-named-conditional-group-exists-replacement-absent-str",
            "pattern-sub-template-named-conditional-group-exists-replacement-present-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-no-else-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-no-else-replacement-present-str",
            "module-subn-conditional-group-exists-no-else-replacement-absent-str",
            "pattern-sub-conditional-group-exists-no-else-replacement-present-str",
            "pattern-subn-conditional-group-exists-no-else-replacement-absent-str",
            "module-sub-named-conditional-group-exists-no-else-replacement-present-str",
            "module-subn-named-conditional-group-exists-no-else-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-no-else-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-no-else-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-empty-else-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-empty-else-replacement-present-str",
            "module-subn-conditional-group-exists-empty-else-replacement-absent-str",
            "pattern-sub-conditional-group-exists-empty-else-replacement-present-str",
            "pattern-subn-conditional-group-exists-empty-else-replacement-absent-str",
            "module-sub-named-conditional-group-exists-empty-else-replacement-present-str",
            "module-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-empty-else-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-empty-yes-else-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
            "module-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
            "pattern-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
            "pattern-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
            "module-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
            "module-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-fully-empty-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-fully-empty-replacement-present-str",
            "module-subn-conditional-group-exists-fully-empty-replacement-absent-str",
            "pattern-sub-conditional-group-exists-fully-empty-replacement-present-str",
            "pattern-subn-conditional-group-exists-fully-empty-replacement-absent-str",
            "module-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
            "module-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-alternation-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-alternation-replacement-present-first-arm-str",
            "module-subn-conditional-group-exists-alternation-replacement-present-second-arm-str",
            "pattern-sub-conditional-group-exists-alternation-replacement-absent-first-arm-str",
            "pattern-subn-conditional-group-exists-alternation-replacement-absent-second-arm-str",
            "module-sub-named-conditional-group-exists-alternation-replacement-present-first-arm-str",
            "module-subn-named-conditional-group-exists-alternation-replacement-present-second-arm-str",
            "pattern-sub-named-conditional-group-exists-alternation-replacement-absent-first-arm-str",
            "pattern-subn-named-conditional-group-exists-alternation-replacement-absent-second-arm-str",
        ),
    ),
    "conditional-group-exists-nested-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-nested-replacement-present-str",
            "module-subn-conditional-group-exists-nested-replacement-absent-str",
            "pattern-sub-conditional-group-exists-nested-replacement-present-str",
            "pattern-subn-conditional-group-exists-nested-replacement-absent-str",
            "module-sub-named-conditional-group-exists-nested-replacement-present-str",
            "module-subn-named-conditional-group-exists-nested-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-nested-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-nested-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-quantified-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-quantified-replacement-present-str",
            "module-subn-conditional-group-exists-quantified-replacement-absent-str",
            "pattern-sub-conditional-group-exists-quantified-replacement-present-str",
            "pattern-subn-conditional-group-exists-quantified-replacement-absent-str",
            "module-sub-named-conditional-group-exists-quantified-replacement-present-str",
            "module-subn-named-conditional-group-exists-quantified-replacement-absent-str",
            "pattern-sub-named-conditional-group-exists-quantified-replacement-present-str",
            "pattern-subn-named-conditional-group-exists-quantified-replacement-absent-str",
        ),
    ),
    "conditional-group-exists-quantified-alternation-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-conditional-group-exists-quantified-alternation-replacement-present-first-arm-str",
            "module-subn-conditional-group-exists-quantified-alternation-replacement-present-second-arm-str",
            "pattern-sub-conditional-group-exists-quantified-alternation-replacement-absent-first-arm-str",
            "pattern-subn-conditional-group-exists-quantified-alternation-replacement-absent-second-arm-str",
            "module-sub-named-conditional-group-exists-quantified-alternation-replacement-present-first-arm-str",
            "module-subn-named-conditional-group-exists-quantified-alternation-replacement-present-second-arm-str",
            "pattern-sub-named-conditional-group-exists-quantified-alternation-replacement-absent-first-arm-str",
            "pattern-subn-named-conditional-group-exists-quantified-alternation-replacement-absent-second-arm-str",
        ),
    ),
}


WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS = {
    "broader-range-wider-ranged-repeat-quantified-group-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "broader-range-wider-ranged-repeat-numbered-group-compile-metadata-str",
            "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
            "broader-range-wider-ranged-repeat-numbered-group-pattern-fullmatch-lower-bound-str",
            "broader-range-wider-ranged-repeat-named-group-compile-metadata-str",
            "broader-range-wider-ranged-repeat-named-group-module-search-upper-bound-str",
            "broader-range-wider-ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
        ),
    ),
    "wider-ranged-repeat-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "wider-ranged-repeat-quantified-group-alternation-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "broader-range-wider-ranged-repeat-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-upper-bound-c-branch-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-bytes",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-upper-bound-c-branch-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
            "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
            "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-bytes",
            "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-short-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-mixed-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-overflow-workflow-bytes",
        ),
    ),
    "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-mixed-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-short-then-long-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-mixed-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-invalid-tail-bytes",
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-overflow-bytes",
        ),
    ),
}


NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS = {
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-bc-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-de-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-upper-bound-all-de-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-missing-trailing-d-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-lower-bound-bc-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-lower-bound-de-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-upper-bound-all-de-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-short-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-overflow-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-mixed-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-e-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-short-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-all-de-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-mixed-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-bytes",
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-overflow-workflow-bytes",
        ),
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
    ),
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-upper-bound-b-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-mixed-branches-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-upper-bound-b-branch-first-match-only-bytes",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-mixed-branches-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-bytes",
        ),
        tracked_report_freshness_sample=True,
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-fourth-repetition-b-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-mixed-branches-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-fourth-repetition-b-branch-first-match-only-bytes",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-mixed-branches-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-first-match-only-long-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-bytes",
        ),
    ),
}


OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS = {
    "open-ended-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
            "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-bytes",
            "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-bytes",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-second-repetition-bc-bc-bytes",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-second-repetition-bc-de-bytes",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-bytes",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-below-lower-bound-bytes",
            "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-invalid-branch-bytes",
            "open-ended-quantified-group-alternation-named-compile-metadata-bytes",
            "open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-bytes",
            "open-ended-quantified-group-alternation-named-module-search-lower-bound-de-bytes",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-second-repetition-bc-de-bytes",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-bytes",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-bytes",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-below-lower-bound-bytes",
            "open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-invalid-branch-bytes",
        ),
    ),
    "nested-open-ended-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "nested-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
            "nested-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-bytes",
            "nested-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-bytes",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-bytes",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-fourth-repetition-de-bytes",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-bytes",
            "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-missing-trailing-d-bytes",
            "nested-open-ended-quantified-group-alternation-named-compile-metadata-bytes",
            "nested-open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-bytes",
            "nested-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-bytes",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-bytes",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-bytes",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-short-bytes",
            "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-missing-trailing-d-bytes",
        ),
    ),
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "module-subn-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "pattern-subn-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
            "module-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "module-subn-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
            "pattern-subn-callable-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
        ),
    ),
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
            "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
            "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
            "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
            "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-str",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-bytes",
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-str",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-c-branch-first-match-only-bytes",
            "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
            "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-first-match-only-b-branch-bytes",
            "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-bytes",
            "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-bytes",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-bytes",
        ),
    ),
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-mixed-branches-bytes",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-mixed-branches-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-bytes",
        ),
    ),
    "broader-range-open-ended-quantified-group-alternation-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-second-repetition-bc-de-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-fourth-repetition-de-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-one-repetition-bytes",
            "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-zero-repetition-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-second-repetition-bc-de-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-one-repetition-bytes",
            "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-zero-repetition-bytes",
        ),
    ),
    "open-ended-quantified-group-alternation-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
            "open-ended-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
            "open-ended-quantified-group-alternation-conditional-named-module-search-absent-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-bytes",
            "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-bytes",
        ),
    ),
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-one-repetition-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-absent-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-bytes",
            "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-bytes",
        ),
    ),
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-long-branch-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-short-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-overlap-tail-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-bytes",
            "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-bytes",
        ),
    ),
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows": CorrectnessScorecardManifestExpectation(
        representative_case_ids=(
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
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-short-only-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-one-repetition-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-short-only-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-short-then-long-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-one-repetition-bytes",
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-bytes",
        ),
    ),
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


@dataclass(frozen=True)
class CorrectnessScorecardSuiteDefinition:
    suite_id: str
    expectation_label: str
    expectation_table: dict[str, CorrectnessScorecardManifestExpectation]


CORRECTNESS_SCORECARD_SUITE_REGISTRY = (
    CorrectnessScorecardSuiteDefinition(
        suite_id="combined",
        expectation_label="combined correctness",
        expectation_table=COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="branch-local-backreference",
        expectation_label="branch-local-backreference correctness scorecard",
        expectation_table=BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="conditional-replacement",
        expectation_label="conditional replacement correctness scorecard",
        expectation_table=CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="conditional-alternation",
        expectation_label="conditional-alternation correctness scorecard",
        expectation_table=CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="conditional-nested-quantified",
        expectation_label="conditional nested/quantified correctness scorecard",
        expectation_table=CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="quantified-alternation",
        expectation_label="quantified-alternation correctness scorecard",
        expectation_table=QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="open-ended-quantified-group",
        expectation_label="open-ended quantified-group scorecard",
        expectation_table=OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id="wider-ranged-repeat-quantified-group",
        expectation_label="wider-ranged-repeat quantified-group scorecard",
        expectation_table=WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    ),
    CorrectnessScorecardSuiteDefinition(
        suite_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-"
            "alternation"
        ),
        expectation_label=(
            "nested broader-range wider-ranged-repeat quantified-group "
            "alternation scorecard"
        ),
        expectation_table=(
            NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS
        ),
    ),
)
_CORRECTNESS_SCORECARD_SUITES_BY_ID = {
    suite.suite_id: suite for suite in CORRECTNESS_SCORECARD_SUITE_REGISTRY
}
if len(_CORRECTNESS_SCORECARD_SUITES_BY_ID) != len(CORRECTNESS_SCORECARD_SUITE_REGISTRY):
    raise AssertionError("duplicate correctness scorecard suite ids in registry")


def _sorted_unique_strings(values: object) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values if value is not None}))


def _expected_target_manifest_ids(
    expectations: dict[str, CorrectnessScorecardManifestExpectation],
    *,
    expectation_label: str,
) -> tuple[str, ...]:
    target_manifest_ids = tuple(
        manifest.manifest_id
        for manifest in published_fixture_manifests()
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
    expectation_table: dict[str, CorrectnessScorecardManifestExpectation],
) -> CorrectnessScorecardExpectation:
    selected_paths: list[pathlib.Path] = []
    selected_manifests: list[FixtureManifest] = []
    selected_cases: list[FixtureCase] = []
    target_cases: tuple[FixtureCase, ...] | None = None
    target_manifest: FixtureManifest | None = None

    for manifest in published_fixture_manifests():
        selected_paths.append(manifest.path)
        selected_manifests.append(manifest)
        selected_cases.extend(manifest.cases)
        if manifest.manifest_id == target_manifest_id:
            target_manifest = manifest
            target_cases = tuple(manifest.cases)
            break

    if target_manifest is None or target_cases is None:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in DEFAULT_FIXTURE_PATHS"
        )

    manifest_expectation = expectation_table.get(target_manifest_id)
    if manifest_expectation is None:
        raise AssertionError(f"missing correctness expectation for {target_manifest_id!r}")

    representative_case_ids = manifest_expectation.representative_case_ids
    target_cases_by_id = {case.case_id: case for case in target_cases}
    missing_case_ids = sorted(
        case_id for case_id in representative_case_ids if case_id not in target_cases_by_id
    )
    if missing_case_ids:
        raise AssertionError(
            f"missing representative cases for {target_manifest_id!r}: {missing_case_ids}"
        )

    selected_cases_by_manifest_id = {
        manifest.manifest_id: tuple(manifest.cases)
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


def tracked_correctness_scorecard_suites(
) -> tuple[CorrectnessScorecardSuiteDefinition, ...]:
    return CORRECTNESS_SCORECARD_SUITE_REGISTRY


def _correctness_scorecard_suite_definition(
    suite_id: str,
) -> CorrectnessScorecardSuiteDefinition:
    suite = _CORRECTNESS_SCORECARD_SUITES_BY_ID.get(suite_id)
    if suite is None:
        raise AssertionError(
            f"unknown correctness scorecard suite {suite_id!r}; "
            f"expected one of {sorted(_CORRECTNESS_SCORECARD_SUITES_BY_ID)}"
        )
    return suite


@lru_cache(maxsize=1)
def _tracked_report_freshness_manifest_ids() -> tuple[str, ...]:
    manifest_ids: list[str] = []
    seen_manifest_ids: set[str] = set()

    for suite in CORRECTNESS_SCORECARD_SUITE_REGISTRY:
        for manifest_id, expectation in suite.expectation_table.items():
            if not expectation.tracked_report_freshness_sample:
                continue
            if manifest_id in seen_manifest_ids:
                raise AssertionError(
                    "duplicate tracked report freshness manifest owner for "
                    f"{manifest_id!r}"
                )
            seen_manifest_ids.add(manifest_id)
            manifest_ids.append(manifest_id)

    return tuple(manifest_ids)


@lru_cache(maxsize=1)
def _tracked_report_freshness_manifests() -> tuple[FixtureManifest, ...]:
    freshness_manifest_ids = set(_tracked_report_freshness_manifest_ids())
    manifests = tuple(
        manifest
        for manifest in published_fixture_manifests()
        if manifest.manifest_id in freshness_manifest_ids
    )
    missing_manifest_ids = sorted(
        freshness_manifest_ids - {manifest.manifest_id for manifest in manifests}
    )
    if missing_manifest_ids:
        raise AssertionError(
            "tracked report freshness sample manifests drifted from "
            f"published_fixture_manifests(): missing {missing_manifest_ids}"
        )
    return manifests


@lru_cache(maxsize=None)
def correctness_scorecard_target_manifest_ids(suite_id: str) -> tuple[str, ...]:
    suite = _correctness_scorecard_suite_definition(suite_id)
    return _expected_target_manifest_ids(
        suite.expectation_table,
        expectation_label=suite.expectation_label,
    )


@lru_cache(maxsize=None)
def correctness_scorecard_case(
    suite_id: str,
    target_manifest_id: str,
) -> CorrectnessScorecardExpectation:
    suite = _correctness_scorecard_suite_definition(suite_id)
    return _build_scorecard_expectation(
        target_manifest_id,
        suite.expectation_table,
    )

def _correctness_summary(cases: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "executed_cases": len(cases),
        "failed_cases": sum(1 for case in cases if case["comparison"] == "fail"),
        "passed_cases": sum(1 for case in cases if case["comparison"] == "pass"),
        "skipped_cases": sum(
            1 for case in cases if case["comparison"] == "skipped"
        ),
        "total_cases": len(cases),
        "unimplemented_cases": sum(
            1 for case in cases if case["comparison"] == "unimplemented"
        ),
    }


def _correctness_observation_summary(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    warning_case_count = 0
    exception_case_count = 0
    warning_categories: dict[str, int] = {}
    exception_types: dict[str, int] = {}

    for observation in observations:
        outcome = str(observation["outcome"])
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

        warnings_payload = observation.get("warnings") or []
        if warnings_payload:
            warning_case_count += 1
            for warning_record in warnings_payload:
                category = str(warning_record["category"])
                warning_categories[category] = warning_categories.get(category, 0) + 1

        exception = observation.get("exception")
        if exception is not None:
            exception_case_count += 1
            exception_type = str(exception["type"])
            exception_types[exception_type] = exception_types.get(exception_type, 0) + 1

    return {
        "outcomes": dict(sorted(outcomes.items())),
        "warning_case_count": warning_case_count,
        "exception_case_count": exception_case_count,
        "warning_categories": dict(sorted(warning_categories.items())),
        "exception_types": dict(sorted(exception_types.items())),
    }


def _correctness_diagnostics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_adapter": {
            "cpython": _correctness_observation_summary(
                [case["observations"]["cpython"] for case in cases]
            ),
            "rebar": _correctness_observation_summary(
                [case["observations"]["rebar"] for case in cases]
            ),
        }
    }


def _correctness_cases_for_suite(
    scorecard: dict[str, Any],
    suite: dict[str, Any],
) -> list[dict[str, Any]]:
    suite_cases = [
        case
        for case in scorecard["cases"]
        if case["manifest_id"] in suite["manifest_ids"] and case["layer"] == suite["layer"]
    ]
    if suite["operations"]:
        suite_cases = [
            case for case in suite_cases if case["operation"] in suite["operations"]
        ]
    if suite["text_models"]:
        suite_cases = [
            case
            for case in suite_cases
            if case.get("text_model") in suite["text_models"]
        ]
    return suite_cases


def find_correctness_suite_record(
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    for suite in scorecard["suites"]:
        if str(suite["id"]) == suite_id:
            return suite
    raise AssertionError(f"missing correctness suite record for {suite_id!r}")


def find_correctness_case_record(
    scorecard: dict[str, Any],
    case_id: str,
) -> dict[str, Any]:
    for case in scorecard["cases"]:
        if str(case["id"]) == case_id:
            return case
    raise AssertionError(f"missing correctness case record for {case_id!r}")


def assert_correctness_case_record_matches(
    testcase: Any,
    actual_case: dict[str, Any],
    expected_case: dict[str, Any],
) -> None:
    for key in (
        "id",
        "manifest_id",
        "suite_id",
        "layer",
        "family",
        "operation",
        "notes",
        "categories",
        "comparison",
        "comparison_notes",
        "observations",
    ):
        testcase.assertEqual(actual_case.get(key), expected_case.get(key))

    for key in (
        "text_model",
        "pattern",
        "flags",
        "helper",
        "kwargs",
        "use_compiled_pattern",
    ):
        testcase.assertEqual(actual_case.get(key), expected_case.get(key))

    actual_args = actual_case.get("args")
    expected_args = expected_case.get("args")
    testcase.assertEqual(bool(actual_args), bool(expected_args))
    if not actual_args or not expected_args:
        return

    testcase.assertEqual(len(actual_args), len(expected_args))
    for actual_arg, expected_arg in zip(actual_args, expected_args):
        if (
            isinstance(actual_arg, dict)
            and isinstance(expected_arg, dict)
            and actual_arg.get("type") == "callable"
            and expected_arg.get("type") == "callable"
        ):
            testcase.assertEqual(actual_arg["type"], expected_arg["type"])
            testcase.assertEqual(actual_arg["qualname"], expected_arg["qualname"])
            continue
        testcase.assertEqual(actual_arg, expected_arg)


def _assert_correctness_suite_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_id: str,
) -> dict[str, Any]:
    suite = find_correctness_suite_record(scorecard, suite_id)
    suite_cases = _correctness_cases_for_suite(scorecard, suite)
    testcase.assertEqual(suite["case_count"], len(suite_cases))
    testcase.assertEqual(suite["summary"], _correctness_summary(suite_cases))
    testcase.assertEqual(suite["diagnostics"], _correctness_diagnostics(suite_cases))
    return suite


def assert_correctness_suites_present(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_ids: Iterable[str],
) -> tuple[dict[str, Any], ...]:
    return tuple(
        _assert_correctness_suite_summary_consistent(testcase, scorecard, suite_id)
        for suite_id in suite_ids
    )


def assert_correctness_report_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    testcase.assertEqual(summary, scorecard["summary"])
    testcase.assertEqual(scorecard["summary"], _correctness_summary(scorecard["cases"]))
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "correctness")
    testcase.assertEqual(scorecard["phase"], expected_phase)

    baseline = scorecard["baseline"]
    expected_baseline = {
        **build_cpython_baseline(version_family="3.12.x"),
        "re_module": "re",
    }
    for key, expected_value in expected_baseline.items():
        testcase.assertEqual(baseline[key], expected_value)
    testcase.assertEqual(baseline["oracle"], "cpython-stdlib-re")
    testcase.assertEqual(baseline["target_module"], "rebar")
    testcase.assertEqual(scorecard["diagnostics"], _correctness_diagnostics(scorecard["cases"]))
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


def assert_correctness_fixture_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_paths: tuple[str, ...],
    expected_case_count: int,
) -> None:
    fixtures = scorecard["fixtures"]
    testcase.assertEqual(fixtures["manifest_count"], len(expected_manifest_ids))
    testcase.assertEqual(fixtures["manifest_ids"], list(expected_manifest_ids))
    testcase.assertEqual(fixtures["paths"], list(expected_paths))
    testcase.assertEqual(fixtures["case_count"], expected_case_count)
    if len(expected_manifest_ids) == 1:
        testcase.assertEqual(fixtures["manifest_id"], expected_manifest_ids[0])
        testcase.assertEqual(fixtures["path"], expected_paths[0])


def assert_correctness_layer_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    layer_id: str,
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_operations: tuple[str, ...],
    expected_text_models: tuple[str, ...],
) -> dict[str, Any]:
    layer = scorecard["layers"][layer_id]
    layer_cases = [case for case in scorecard["cases"] if case["layer"] == layer_id]
    testcase.assertEqual(layer["case_count"], len(layer_cases))
    testcase.assertEqual(layer["summary"], _correctness_summary(layer_cases))
    testcase.assertEqual(layer["diagnostics"], _correctness_diagnostics(layer_cases))
    testcase.assertEqual(layer["manifest_ids"], list(expected_manifest_ids))
    testcase.assertEqual(layer["operations"], list(expected_operations))
    testcase.assertEqual(layer["text_models"], list(expected_text_models))
    return layer


def assert_correctness_suite_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    suite_id: str,
    *,
    expected_manifest_ids: tuple[str, ...],
    expected_families: tuple[str, ...],
    expected_operations: tuple[str, ...],
    expected_text_models: tuple[str, ...],
) -> dict[str, Any]:
    suite = _assert_correctness_suite_summary_consistent(testcase, scorecard, suite_id)
    testcase.assertEqual(suite["manifest_ids"], list(expected_manifest_ids))
    testcase.assertEqual(suite["families"], list(expected_families))
    testcase.assertEqual(suite["operations"], list(expected_operations))
    testcase.assertEqual(suite["text_models"], list(expected_text_models))
    return suite


def assert_correctness_suite_case_accounting(
    testcase: Any,
    suite: dict[str, Any],
    *,
    expected_case_count: int,
) -> None:
    testcase.assertEqual(suite["summary"]["total_cases"], expected_case_count)
    testcase.assertEqual(suite["summary"]["failed_cases"], 0)
    testcase.assertEqual(suite["summary"]["skipped_cases"], 0)
    testcase.assertEqual(
        suite["summary"]["passed_cases"] + suite["summary"]["unimplemented_cases"],
        expected_case_count,
    )

EXPECTED_SUITE_TABLES = {
    "combined": COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
    "branch-local-backreference": BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "conditional-replacement": CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "conditional-alternation": CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "conditional-nested-quantified": CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "quantified-alternation": QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "open-ended-quantified-group": OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    "wider-ranged-repeat-quantified-group": WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation": (
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS
    ),
}

MIXED_TEXT_MIRROR_EXPECTATION_TABLES = {
    "open-ended-quantified-group": OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    "quantified-alternation": QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "wider-ranged-repeat-quantified-group": (
        WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS
    ),
}


@lru_cache(maxsize=1)
def _build_rebar_extension() -> None:
    subprocess.run(
        ["cargo", "build", "-p", "rebar-cpython"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def assert_correctness_scorecard_suite(
    testcase: unittest.TestCase,
    *,
    target_manifest_ids: Iterable[str],
    case_factory: Callable[[str], CorrectnessScorecardExpectation],
) -> None:
    target_manifest_ids = tuple(target_manifest_ids)
    _build_rebar_extension()
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    for target_manifest_id in target_manifest_ids:
        with testcase.subTest(manifest_id=target_manifest_id):
            case = case_factory(target_manifest_id)
            summary, scorecard = run_harness_scorecard(
                "rebar_harness.correctness",
                [
                    "--fixtures",
                    *(str(path) for path in case.fixture_paths),
                ],
                report_name="correctness.json",
            )

            assert_correctness_report_contract(
                testcase,
                scorecard,
                summary,
                expected_phase=case.expected_phase,
                tracked_report_path=TRACKED_REPORT_PATH,
            )
            assert_correctness_fixture_contract(
                testcase,
                scorecard,
                expected_manifest_ids=case.expected_fixture_manifest_ids,
                expected_paths=case.expected_fixture_paths,
                expected_case_count=case.expected_fixture_case_count,
            )
            testcase.assertEqual(
                [suite["id"] for suite in scorecard["suites"]],
                list(case.expected_cumulative_suite_ids),
            )
            testcase.assertEqual(
                tuple(scorecard["layers"]),
                tuple(
                    layer_expectation.layer_id
                    for layer_expectation in case.layer_expectations
                ),
            )
            for layer_expectation in case.layer_expectations:
                assert_correctness_layer_contract(
                    testcase,
                    scorecard,
                    layer_expectation.layer_id,
                    expected_manifest_ids=layer_expectation.expected_manifest_ids,
                    expected_operations=layer_expectation.expected_operations,
                    expected_text_models=layer_expectation.expected_text_models,
                )
            workflow_suite = assert_correctness_suite_contract(
                testcase,
                scorecard,
                case.target_suite_id,
                expected_manifest_ids=(case.target_manifest_id,),
                expected_families=case.target_suite_families,
                expected_operations=case.target_suite_operations,
                expected_text_models=case.target_suite_text_models,
            )
            assert_correctness_suite_case_accounting(
                testcase,
                workflow_suite,
                expected_case_count=case.target_manifest_case_count,
            )
            assert_correctness_suites_present(
                testcase,
                scorecard,
                case.expected_suite_ids[1:],
            )

            for fixture_case in case.representative_cases:
                with testcase.subTest(
                    manifest_id=target_manifest_id,
                    case_id=fixture_case.case_id,
                ):
                    expected_case = evaluate_case(
                        fixture_case,
                        cpython_adapter,
                        rebar_adapter,
                    )
                    assert_correctness_case_record_matches(
                        testcase,
                        find_correctness_case_record(scorecard, fixture_case.case_id),
                        expected_case,
                    )


def _fixture_manifest(
    *,
    filename: str,
    manifest_id: str,
    layer: str,
    suite_id: str,
) -> correctness.FixtureManifest:
    return correctness.FixtureManifest(
        path=REPO_ROOT / "tests" / "conformance" / "fixtures" / filename,
        manifest_id=manifest_id,
        layer=layer,
        suite_id=suite_id,
        schema_version=1,
        defaults={},
        cases=[],
    )


def _observation(
    adapter: str,
    operation: str,
    outcome: str,
    *,
    warnings: list[dict[str, str]] | None = None,
    result: object = None,
    exception: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "adapter": adapter,
        "operation": operation,
        "outcome": outcome,
        "warnings": [] if warnings is None else warnings,
        "result": result,
        "exception": exception,
    }


def _case_result(
    *,
    case_id: str,
    manifest_id: str,
    suite_id: str,
    layer: str,
    family: str,
    operation: str,
    comparison: str,
    text_model: str,
    cpython_observation: dict[str, object],
    rebar_observation: dict[str, object],
) -> dict[str, object]:
    return {
        "id": case_id,
        "manifest_id": manifest_id,
        "suite_id": suite_id,
        "layer": layer,
        "family": family,
        "operation": operation,
        "notes": [],
        "categories": [],
        "comparison": comparison,
        "comparison_notes": [],
        "text_model": text_model,
        "observations": {
            "cpython": cpython_observation,
            "rebar": rebar_observation,
        },
    }


def _adapter_contract_case(
    *,
    case_id: str,
    operation: str,
    helper: str | None = None,
    args: list[Any] | None = None,
) -> FixtureCase:
    observed_args = [] if args is None else list(args)
    return FixtureCase(
        case_id=case_id,
        manifest_id="adapter-contract",
        suite_id="adapter.contract",
        layer="regression_and_coverage",
        family="adapter_contracts",
        operation=operation,
        notes=[],
        categories=["adapter-contract"],
        pattern="abc",
        flags=0,
        text_model="str",
        pattern_encoding="latin-1",
        helper=helper,
        source_args=list(observed_args),
        source_kwargs={},
        args=observed_args,
        kwargs={},
    )


class _WarningModuleCallFailureModule:
    def search(self, pattern: str, string: str) -> object:
        warnings.warn("module helper warning", RuntimeWarning)
        raise NotImplementedError("module helper todo")


class _WarningModuleCallExceptionModule:
    def search(self, pattern: str, string: str) -> object:
        warnings.warn("module helper warning", RuntimeWarning)
        raise TypeError("module helper failure")


class _WarningCompileFailureModule:
    def __init__(self, *, message: str) -> None:
        self._message = message

    def compile(self, pattern: str, flags: int = 0) -> object:
        warnings.warn("compile warning", FutureWarning)
        raise NotImplementedError(self._message)

    def purge(self) -> None:
        return None


class _WarningCompileExceptionModule:
    def __init__(self, *, message: str) -> None:
        self._message = message

    def compile(self, pattern: str, flags: int = 0) -> object:
        warnings.warn("compile warning", FutureWarning)
        raise TypeError(self._message)

    def purge(self) -> None:
        return None


class _WarningPatternCallFailurePattern:
    def search(self, string: str) -> object:
        warnings.warn("pattern helper warning", UserWarning)
        raise ValueError("pattern helper failure")


class _WarningPatternCallFailureModule:
    def compile(self, pattern: str, flags: int = 0) -> object:
        return _WarningPatternCallFailurePattern()


PARSER_MANIFEST = _fixture_manifest(
    filename="parser_matrix.py",
    manifest_id="parser-matrix",
    layer="parser_acceptance_and_diagnostics",
    suite_id="parser.compile",
)
WORKFLOW_MANIFEST = _fixture_manifest(
    filename="module_workflow_surface.py",
    manifest_id="module-workflow-surface",
    layer="module_workflow",
    suite_id="workflow.synthetic",
)
MANIFESTS = (PARSER_MANIFEST, WORKFLOW_MANIFEST)
CASE_RESULTS = [
    _case_result(
        case_id="parser-str-pass",
        manifest_id=PARSER_MANIFEST.manifest_id,
        suite_id=PARSER_MANIFEST.suite_id,
        layer=PARSER_MANIFEST.layer,
        family="parser_literals",
        operation="compile",
        comparison="pass",
        text_model="str",
        cpython_observation=_observation(
            "cpython.re",
            "compile",
            "success",
            result={"pattern": "abc"},
        ),
        rebar_observation=_observation(
            "rebar",
            "compile",
            "success",
            result={"pattern": "abc"},
        ),
    ),
    _case_result(
        case_id="parser-bytes-fail",
        manifest_id=PARSER_MANIFEST.manifest_id,
        suite_id=PARSER_MANIFEST.suite_id,
        layer=PARSER_MANIFEST.layer,
        family="parser_diagnostics",
        operation="compile",
        comparison="fail",
        text_model="bytes",
        cpython_observation=_observation(
            "cpython.re",
            "compile",
            "success",
            warnings=[
                {
                    "category": "FutureWarning",
                    "message": "ambiguous nested set",
                }
            ],
            result={"pattern": "a[b]"},
        ),
        rebar_observation=_observation(
            "rebar",
            "compile",
            "exception",
            warnings=[
                {
                    "category": "RuntimeWarning",
                    "message": "native bridge mismatch",
                }
            ],
            exception={"type": "error", "message": "bad range"},
        ),
    ),
    _case_result(
        case_id="workflow-bytes-unimplemented",
        manifest_id=WORKFLOW_MANIFEST.manifest_id,
        suite_id=WORKFLOW_MANIFEST.suite_id,
        layer=WORKFLOW_MANIFEST.layer,
        family="workflow_search",
        operation="module_call",
        comparison="unimplemented",
        text_model="bytes",
        cpython_observation=_observation(
            "cpython.re",
            "module_call",
            "success",
            result={"matched": True},
        ),
        rebar_observation=_observation(
            "rebar",
            "module_call",
            "unimplemented",
            warnings=[
                {
                    "category": "DeprecationWarning",
                    "message": "temporary shim",
                }
            ],
            exception={"type": "NotImplementedError", "message": "todo"},
        ),
    ),
    _case_result(
        case_id="workflow-str-pass",
        manifest_id=WORKFLOW_MANIFEST.manifest_id,
        suite_id=WORKFLOW_MANIFEST.suite_id,
        layer=WORKFLOW_MANIFEST.layer,
        family="workflow_search",
        operation="pattern_call",
        comparison="pass",
        text_model="str",
        cpython_observation=_observation(
            "cpython.re",
            "pattern_call",
            "success",
            result={"matched": False},
        ),
        rebar_observation=_observation(
            "rebar",
            "pattern_call",
            "success",
            result={"matched": False},
        ),
    ),
]


class CorrectnessBuilderContractTest(unittest.TestCase):
    maxDiff = None

    def test_adapter_module_call_preserves_warning_payloads_and_unimplemented_mapping(
        self,
    ) -> None:
        case = _adapter_contract_case(
            case_id="adapter-module-call-contract",
            operation="module_call",
            helper="search",
            args=["abc", "zzabczz"],
        )

        for adapter_cls in (CpythonReAdapter, RebarAdapter):
            with self.subTest(adapter=adapter_cls.adapter_name):
                adapter = adapter_cls()
                adapter.module = _WarningModuleCallFailureModule()

                observation = adapter.observe(case)

                self.assertEqual(observation["adapter"], adapter_cls.adapter_name)
                self.assertEqual(observation["operation"], "module_call")
                self.assertEqual(observation["outcome"], "unimplemented")
                self.assertEqual(
                    observation["warnings"],
                    [
                        {
                            "category": "RuntimeWarning",
                            "message": "module helper warning",
                        }
                    ],
                )
                self.assertIsNone(observation["result"])
                self.assertEqual(
                    observation["exception"],
                    {
                        "type": "NotImplementedError",
                        "message": "module helper todo",
                    },
                )

    def test_adapter_module_call_preserves_warning_payloads_for_generic_exceptions(
        self,
    ) -> None:
        case = _adapter_contract_case(
            case_id="adapter-module-call-exception-contract",
            operation="module_call",
            helper="search",
            args=["abc", "zzabczz"],
        )

        for adapter_cls in (CpythonReAdapter, RebarAdapter):
            with self.subTest(adapter=adapter_cls.adapter_name):
                adapter = adapter_cls()
                adapter.module = _WarningModuleCallExceptionModule()

                observation = adapter.observe(case)

                self.assertEqual(observation["adapter"], adapter_cls.adapter_name)
                self.assertEqual(observation["operation"], "module_call")
                self.assertEqual(observation["outcome"], "exception")
                self.assertEqual(
                    observation["warnings"],
                    [
                        {
                            "category": "RuntimeWarning",
                            "message": "module helper warning",
                        }
                    ],
                )
                self.assertIsNone(observation["result"])
                self.assertEqual(
                    observation["exception"],
                    {
                        "type": "TypeError",
                        "message": "module helper failure",
                    },
                )

    def test_adapter_compile_observation_preserves_warning_payloads_and_notimplemented_mapping(
        self,
    ) -> None:
        case = _adapter_contract_case(
            case_id="adapter-compile-contract",
            operation="compile",
        )

        for adapter_cls, expected_outcome in (
            (CpythonReAdapter, "exception"),
            (RebarAdapter, "unimplemented"),
        ):
            with self.subTest(adapter=adapter_cls.adapter_name):
                adapter = adapter_cls()
                adapter.module = _WarningCompileFailureModule(
                    message="compile helper todo"
                )

                observation = adapter.observe(case)

                self.assertEqual(observation["adapter"], adapter_cls.adapter_name)
                self.assertEqual(observation["operation"], "compile")
                self.assertEqual(observation["outcome"], expected_outcome)
                self.assertEqual(
                    observation["warnings"],
                    [
                        {
                            "category": "FutureWarning",
                            "message": "compile warning",
                        }
                    ],
                )
                self.assertIsNone(observation["result"])
                self.assertEqual(
                    observation["exception"],
                    {
                        "type": "NotImplementedError",
                        "message": "compile helper todo",
                    },
                )

    def test_adapter_cache_workflow_preserves_warning_payloads_and_notimplemented_mapping(
        self,
    ) -> None:
        case = _adapter_contract_case(
            case_id="adapter-cache-workflow-contract",
            operation="cache_workflow",
        )

        for adapter_cls, expected_outcome in (
            (CpythonReAdapter, "exception"),
            (RebarAdapter, "unimplemented"),
        ):
            with self.subTest(adapter=adapter_cls.adapter_name):
                module = _WarningCompileFailureModule(message="cache helper todo")
                adapter = adapter_cls()
                adapter.module = module

                observation = adapter.observe(case)

                self.assertEqual(observation["adapter"], adapter_cls.adapter_name)
                self.assertEqual(observation["operation"], "cache_workflow")
                self.assertEqual(observation["outcome"], expected_outcome)
                self.assertEqual(
                    observation["warnings"],
                    [
                        {
                            "category": "FutureWarning",
                            "message": "compile warning",
                        }
                    ],
                )
                self.assertIsNone(observation["result"])
                self.assertEqual(
                    observation["exception"],
                    {
                        "type": "NotImplementedError",
                        "message": "cache helper todo",
                    },
                )

    def test_adapter_cache_workflow_preserves_warning_payloads_for_generic_exceptions(
        self,
    ) -> None:
        case = _adapter_contract_case(
            case_id="adapter-cache-workflow-exception-contract",
            operation="cache_workflow",
        )

        for adapter_cls in (CpythonReAdapter, RebarAdapter):
            with self.subTest(adapter=adapter_cls.adapter_name):
                adapter = adapter_cls()
                adapter.module = _WarningCompileExceptionModule(
                    message="cache helper failure"
                )

                observation = adapter.observe(case)

                self.assertEqual(observation["adapter"], adapter_cls.adapter_name)
                self.assertEqual(observation["operation"], "cache_workflow")
                self.assertEqual(observation["outcome"], "exception")
                self.assertEqual(
                    observation["warnings"],
                    [
                        {
                            "category": "FutureWarning",
                            "message": "compile warning",
                        }
                    ],
                )
                self.assertIsNone(observation["result"])
                self.assertEqual(
                    observation["exception"],
                    {
                        "type": "TypeError",
                        "message": "cache helper failure",
                    },
                )

    def test_adapter_pattern_call_preserves_warning_payloads_for_generic_exceptions(
        self,
    ) -> None:
        case = _adapter_contract_case(
            case_id="adapter-pattern-call-exception-contract",
            operation="pattern_call",
            helper="search",
            args=["zzabczz"],
        )

        for adapter_cls in (CpythonReAdapter, RebarAdapter):
            with self.subTest(adapter=adapter_cls.adapter_name):
                adapter = adapter_cls()
                adapter.module = _WarningPatternCallFailureModule()

                observation = adapter.observe(case)

                self.assertEqual(observation["adapter"], adapter_cls.adapter_name)
                self.assertEqual(observation["operation"], "pattern_call")
                self.assertEqual(observation["outcome"], "exception")
                self.assertEqual(
                    observation["warnings"],
                    [
                        {
                            "category": "UserWarning",
                            "message": "pattern helper warning",
                        }
                    ],
                )
                self.assertIsNone(observation["result"])
                self.assertEqual(
                    observation["exception"],
                    {
                        "type": "ValueError",
                        "message": "pattern helper failure",
                    },
                )

    def test_normalize_match_metadata_preserves_bytes_named_capture_shape(self) -> None:
        match = re.search(rb"(?P<outer>(ab)?)(?P<inner>c)", b"zabc")

        self.assertIsNotNone(match)
        self.assertEqual(
            correctness.normalize_match_metadata(match),
            {
                "matched": True,
                "group0": {"encoding": "latin-1", "value": "abc"},
                "groups": [
                    {"encoding": "latin-1", "value": "ab"},
                    {"encoding": "latin-1", "value": "ab"},
                    {"encoding": "latin-1", "value": "c"},
                ],
                "groupdict": {
                    "inner": {"encoding": "latin-1", "value": "c"},
                    "outer": {"encoding": "latin-1", "value": "ab"},
                },
                "lastgroup": "inner",
                "lastindex": 3,
                "pos": 0,
                "endpos": 4,
                "span": [1, 4],
                "string_type": "bytes",
                "named_groups": {
                    "inner": {"encoding": "latin-1", "value": "c"},
                    "outer": {"encoding": "latin-1", "value": "ab"},
                },
                "named_group_spans": {
                    "inner": [3, 4],
                    "outer": [1, 3],
                },
                "group1": {"encoding": "latin-1", "value": "ab"},
                "span1": [1, 3],
                "group_spans": [[1, 3], [1, 3], [3, 4]],
            },
        )

    def test_normalize_match_metadata_keeps_missing_optional_named_group_details(
        self,
    ) -> None:
        match = re.fullmatch(r"(?P<word>a)?b", "b")

        self.assertIsNotNone(match)
        self.assertEqual(
            correctness.normalize_match_metadata(match),
            {
                "matched": True,
                "group0": "b",
                "groups": [None],
                "groupdict": {"word": None},
                "lastgroup": None,
                "lastindex": None,
                "pos": 0,
                "endpos": 1,
                "span": [0, 1],
                "string_type": "str",
                "named_groups": {"word": None},
                "named_group_spans": {"word": [-1, -1]},
                "group1": None,
                "span1": [-1, -1],
                "group_spans": [[-1, -1]],
            },
        )

    def test_normalize_value_exhausts_iterators_and_normalizes_nested_bytes(
        self,
    ) -> None:
        iterator = iter([b"ab", {"x": (1, b"y")}])

        self.assertEqual(
            correctness._normalize_value(iterator),
            {
                "items": [
                    {"encoding": "latin-1", "value": "ab"},
                    {"x": [1, {"encoding": "latin-1", "value": "y"}]},
                ],
                "exhausted": True,
            },
        )
        self.assertIsNone(next(iterator, None))

    def test_normalize_warning_and_exception_payloads_preserve_diagnostic_details(
        self,
    ) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warnings.warn("alpha", RuntimeWarning)
            warnings.warn("beta", FutureWarning)

        warning_payload = correctness.normalize_warning_records(caught)
        self.assertEqual(
            warning_payload,
            [
                {"category": "RuntimeWarning", "message": "alpha"},
                {"category": "FutureWarning", "message": "beta"},
            ],
        )

        with self.assertRaises(re.error) as raised:
            re.compile("(")

        exception_payload = correctness.normalize_exception(raised.exception)
        self.assertEqual(exception_payload["type"], "error")
        self.assertIn("missing )", exception_payload["message"])
        self.assertEqual(exception_payload["pos"], 0)
        self.assertEqual(exception_payload["lineno"], 1)
        self.assertEqual(exception_payload["colno"], 1)

    def test_compare_observations_prefers_unimplemented_result(self) -> None:
        comparison, mismatch_notes = correctness.compare_observations(
            {
                "outcome": "success",
                "warnings": [],
                "result": {"status": "ok"},
                "exception": None,
            },
            {
                "outcome": "unimplemented",
                "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
                "result": None,
                "exception": {"type": "NotImplementedError", "message": "todo"},
            },
        )

        self.assertEqual(comparison, "unimplemented")
        self.assertEqual(
            mismatch_notes,
            ["rebar adapter reports support as unimplemented"],
        )

    def test_compare_observations_reports_each_payload_mismatch_in_stable_order(
        self,
    ) -> None:
        comparison, mismatch_notes = correctness.compare_observations(
            {
                "outcome": "success",
                "warnings": [],
                "result": {"status": "ok"},
                "exception": None,
            },
            {
                "outcome": "exception",
                "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
                "result": {"status": "different"},
                "exception": {"type": "TypeError", "message": "boom"},
            },
        )

        self.assertEqual(comparison, "fail")
        self.assertEqual(
            mismatch_notes,
            [
                "outcome mismatch: success != exception",
                "warning payload mismatch",
                "result payload mismatch",
                "exception payload mismatch",
            ],
        )

    def test_build_observation_summary_counts_sorted_outcomes_warnings_and_exceptions(
        self,
    ) -> None:
        observations = [
            {"outcome": "success", "warnings": [], "exception": None},
            {
                "outcome": "exception",
                "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
                "exception": {"type": "TypeError", "message": "boom"},
            },
            {
                "outcome": "exception",
                "warnings": [{"category": "FutureWarning", "message": "beta"}],
                "exception": {"type": "error", "message": "bad"},
            },
            {
                "outcome": "unimplemented",
                "warnings": [{"category": "RuntimeWarning", "message": "gamma"}],
                "exception": None,
            },
        ]

        self.assertEqual(
            correctness.build_observation_summary(observations),
            {
                "outcomes": {
                    "exception": 2,
                    "success": 1,
                    "unimplemented": 1,
                },
                "warning_case_count": 3,
                "exception_case_count": 2,
                "warning_categories": {
                    "FutureWarning": 1,
                    "RuntimeWarning": 2,
                },
                "exception_types": {
                    "TypeError": 1,
                    "error": 1,
                },
            },
        )

    def test_build_summary_counts_each_supported_comparison_bucket(self) -> None:
        case_results = [
            {"comparison": "pass"},
            {"comparison": "pass"},
            {"comparison": "fail"},
            {"comparison": "unimplemented"},
            {"comparison": "skipped"},
        ]

        self.assertEqual(
            correctness.build_summary(case_results),
            {
                "total_cases": 5,
                "executed_cases": 5,
                "passed_cases": 2,
                "failed_cases": 1,
                "unimplemented_cases": 1,
                "skipped_cases": 1,
            },
        )
        self.assertEqual(
            correctness.build_summary(case_results),
            _correctness_summary(case_results),
        )

    def test_build_scorecard_aggregates_correctness_summaries_and_suite_fanout(
        self,
    ) -> None:
        scorecard = correctness.build_scorecard(
            manifests=MANIFESTS,
            case_results=CASE_RESULTS,
        )

        self.assertEqual(scorecard["schema_version"], correctness.REPORT_SCHEMA_VERSION)
        self.assertEqual(scorecard["suite"], "correctness")
        self.assertEqual(scorecard["phase"], "phase3-module-workflow-pack")
        self.assertEqual(scorecard["generator"], "python -m rebar_harness.correctness")
        self.assertTrue(scorecard["generated_at"].endswith("Z"))

        self.assertEqual(
            scorecard["fixtures"],
            {
                "manifest_count": 2,
                "manifest_ids": ["parser-matrix", "module-workflow-surface"],
                "paths": [
                    "tests/conformance/fixtures/parser_matrix.py",
                    "tests/conformance/fixtures/module_workflow_surface.py",
                ],
                "case_count": 4,
            },
        )
        self.assertEqual(
            scorecard["summary"],
            {
                "total_cases": 4,
                "executed_cases": 4,
                "passed_cases": 2,
                "failed_cases": 1,
                "unimplemented_cases": 1,
                "skipped_cases": 0,
            },
        )
        self.assertEqual(
            scorecard["diagnostics"],
            {
                "by_adapter": {
                    "cpython": {
                        "outcomes": {"success": 4},
                        "warning_case_count": 1,
                        "exception_case_count": 0,
                        "warning_categories": {"FutureWarning": 1},
                        "exception_types": {},
                    },
                    "rebar": {
                        "outcomes": {
                            "exception": 1,
                            "success": 2,
                            "unimplemented": 1,
                        },
                        "warning_case_count": 2,
                        "exception_case_count": 2,
                        "warning_categories": {
                            "DeprecationWarning": 1,
                            "RuntimeWarning": 1,
                        },
                        "exception_types": {
                            "NotImplementedError": 1,
                            "error": 1,
                        },
                    },
                }
            },
        )

        self.assertEqual(
            scorecard["layers"],
            {
                "module_workflow": {
                    "manifest_ids": ["module-workflow-surface"],
                    "suite_ids": ["workflow.synthetic"],
                    "case_count": 2,
                    "families": ["workflow_search"],
                    "operations": ["module_call", "pattern_call"],
                    "text_models": ["bytes", "str"],
                    "summary": {
                        "total_cases": 2,
                        "executed_cases": 2,
                        "passed_cases": 1,
                        "failed_cases": 0,
                        "unimplemented_cases": 1,
                        "skipped_cases": 0,
                    },
                    "diagnostics": {
                        "by_adapter": {
                            "cpython": {
                                "outcomes": {"success": 2},
                                "warning_case_count": 0,
                                "exception_case_count": 0,
                                "warning_categories": {},
                                "exception_types": {},
                            },
                            "rebar": {
                                "outcomes": {"success": 1, "unimplemented": 1},
                                "warning_case_count": 1,
                                "exception_case_count": 1,
                                "warning_categories": {"DeprecationWarning": 1},
                                "exception_types": {"NotImplementedError": 1},
                            },
                        }
                    },
                },
                "parser_acceptance_and_diagnostics": {
                    "manifest_ids": ["parser-matrix"],
                    "suite_ids": ["parser.compile"],
                    "case_count": 2,
                    "families": ["parser_diagnostics", "parser_literals"],
                    "operations": ["compile"],
                    "text_models": ["bytes", "str"],
                    "summary": {
                        "total_cases": 2,
                        "executed_cases": 2,
                        "passed_cases": 1,
                        "failed_cases": 1,
                        "unimplemented_cases": 0,
                        "skipped_cases": 0,
                    },
                    "diagnostics": {
                        "by_adapter": {
                            "cpython": {
                                "outcomes": {"success": 2},
                                "warning_case_count": 1,
                                "exception_case_count": 0,
                                "warning_categories": {"FutureWarning": 1},
                                "exception_types": {},
                            },
                            "rebar": {
                                "outcomes": {"exception": 1, "success": 1},
                                "warning_case_count": 1,
                                "exception_case_count": 1,
                                "warning_categories": {"RuntimeWarning": 1},
                                "exception_types": {"error": 1},
                            },
                        }
                    },
                },
            },
        )

        self.assertEqual(
            [suite["id"] for suite in scorecard["suites"]],
            [
                "parser.compile",
                "parser.compile.bytes",
                "parser.compile.str",
                "workflow.synthetic",
                "workflow.synthetic.bytes",
                "workflow.synthetic.str",
                "workflow.synthetic.module_call",
                "workflow.synthetic.pattern_call",
            ],
        )
        self.assertEqual(
            scorecard["suites"][0],
            {
                "id": "parser.compile",
                "layer": "parser_acceptance_and_diagnostics",
                "manifest_ids": ["parser-matrix"],
                "case_count": 2,
                "families": ["parser_diagnostics", "parser_literals"],
                "operations": ["compile"],
                "text_models": ["bytes", "str"],
                "summary": {
                    "total_cases": 2,
                    "executed_cases": 2,
                    "passed_cases": 1,
                    "failed_cases": 1,
                    "unimplemented_cases": 0,
                    "skipped_cases": 0,
                },
                "diagnostics": scorecard["layers"][
                    "parser_acceptance_and_diagnostics"
                ]["diagnostics"],
            },
        )
        self.assertEqual(
            scorecard["suites"][-1],
            {
                "id": "workflow.synthetic.pattern_call",
                "layer": "module_workflow",
                "manifest_ids": ["module-workflow-surface"],
                "case_count": 1,
                "families": ["workflow_search"],
                "operations": ["pattern_call"],
                "text_models": ["str"],
                "summary": {
                    "total_cases": 1,
                    "executed_cases": 1,
                    "passed_cases": 1,
                    "failed_cases": 0,
                    "unimplemented_cases": 0,
                    "skipped_cases": 0,
                },
                "diagnostics": {
                    "by_adapter": {
                        "cpython": {
                            "outcomes": {"success": 1},
                            "warning_case_count": 0,
                            "exception_case_count": 0,
                            "warning_categories": {},
                            "exception_types": {},
                        },
                        "rebar": {
                            "outcomes": {"success": 1},
                            "warning_case_count": 0,
                            "exception_case_count": 0,
                            "warning_categories": {},
                            "exception_types": {},
                        },
                    }
                },
            },
        )

        self.assertEqual(
            scorecard["families"],
            [
                {
                    "id": "parser_diagnostics",
                    "case_count": 1,
                    "layers": ["parser_acceptance_and_diagnostics"],
                    "operations": ["compile"],
                    "text_models": ["bytes"],
                    "summary": {
                        "total_cases": 1,
                        "executed_cases": 1,
                        "passed_cases": 0,
                        "failed_cases": 1,
                        "unimplemented_cases": 0,
                        "skipped_cases": 0,
                    },
                },
                {
                    "id": "parser_literals",
                    "case_count": 1,
                    "layers": ["parser_acceptance_and_diagnostics"],
                    "operations": ["compile"],
                    "text_models": ["str"],
                    "summary": {
                        "total_cases": 1,
                        "executed_cases": 1,
                        "passed_cases": 1,
                        "failed_cases": 0,
                        "unimplemented_cases": 0,
                        "skipped_cases": 0,
                    },
                },
                {
                    "id": "workflow_search",
                    "case_count": 2,
                    "layers": ["module_workflow"],
                    "operations": ["module_call", "pattern_call"],
                    "text_models": ["bytes", "str"],
                    "summary": {
                        "total_cases": 2,
                        "executed_cases": 2,
                        "passed_cases": 1,
                        "failed_cases": 0,
                        "unimplemented_cases": 1,
                        "skipped_cases": 0,
                    },
                },
            ],
        )

    def test_build_fixture_summary_exposes_single_manifest_metadata_on_narrow_runs(
        self,
    ) -> None:
        summary = correctness.build_fixture_summary((WORKFLOW_MANIFEST,), CASE_RESULTS[2:])

        self.assertEqual(
            summary,
            {
                "manifest_count": 1,
                "manifest_ids": ["module-workflow-surface"],
                "paths": ["tests/conformance/fixtures/module_workflow_surface.py"],
                "case_count": 2,
                "path": "tests/conformance/fixtures/module_workflow_surface.py",
                "schema_version": 1,
                "manifest_id": "module-workflow-surface",
            },
        )


class CorrectnessScorecardSuitesTest(unittest.TestCase):
    maxDiff = None

    def _assert_tracked_report_keeps_manifest_fresh(
        self,
        fixture_path: pathlib.Path,
        suite_id: str,
    ) -> None:
        _build_rebar_extension()
        manifest_cases = load_fixture_manifest(fixture_path).cases
        _, expected_scorecard = run_harness_scorecard(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(fixture_path),
            ],
            report_name="correctness.json",
        )
        tracked_scorecard = correctness.SCORECARD_REPORT.load(TRACKED_REPORT_PATH)

        expected_suite = find_correctness_suite_record(expected_scorecard, suite_id)
        tracked_suite = find_correctness_suite_record(tracked_scorecard, suite_id)

        self.assertEqual(tracked_suite["manifest_ids"], expected_suite["manifest_ids"])
        self.assertEqual(tracked_suite["families"], expected_suite["families"])
        self.assertEqual(tracked_suite["operations"], expected_suite["operations"])
        self.assertEqual(tracked_suite["text_models"], expected_suite["text_models"])
        self.assertEqual(tracked_suite["case_count"], expected_suite["case_count"])
        self.assertEqual(tracked_suite["summary"], expected_suite["summary"])
        self.assertEqual(tracked_suite["diagnostics"], expected_suite["diagnostics"])

        for fixture_case in manifest_cases:
            with self.subTest(suite_id=suite_id, case_id=fixture_case.case_id):
                assert_correctness_case_record_matches(
                    self,
                    find_correctness_case_record(
                        tracked_scorecard, fixture_case.case_id
                    ),
                    find_correctness_case_record(expected_scorecard, fixture_case.case_id),
                )

    def test_runner_regenerates_correctness_scorecards(self) -> None:
        for suite in tracked_correctness_scorecard_suites():
            with self.subTest(suite_id=suite.suite_id):
                assert_correctness_scorecard_suite(
                    self,
                    target_manifest_ids=correctness_scorecard_target_manifest_ids(
                        suite.suite_id
                    ),
                    case_factory=partial(correctness_scorecard_case, suite.suite_id),
                )

    def test_tracked_report_keeps_sample_manifests_fresh(
        self,
    ) -> None:
        for manifest in _tracked_report_freshness_manifests():
            with self.subTest(manifest_id=manifest.manifest_id):
                self._assert_tracked_report_keeps_manifest_fresh(
                    manifest.path,
                    manifest.suite_id,
                )


class CorrectnessScorecardRegistryContractTest(unittest.TestCase):
    maxDiff = None

    def _assert_mixed_text_manifests_cover_both_representative_text_models(
        self,
        *,
        suite_id: str,
        expectation_table: object,
    ) -> None:
        manifests_by_id = {
            manifest.manifest_id: manifest
            for manifest in correctness.published_fixture_manifests()
        }
        mixed_text_manifest_ids: list[str] = []

        for manifest_id, manifest_expectation in expectation_table.items():
            manifest = manifests_by_id[manifest_id]
            published_text_models = {case.text_model for case in manifest.cases}
            if published_text_models != {"bytes", "str"}:
                continue

            mixed_text_manifest_ids.append(manifest_id)
            representative_case_id_set = frozenset(
                manifest_expectation.representative_case_ids
            )
            representative_text_models = {
                case.text_model
                for case in manifest.cases
                if case.case_id in representative_case_id_set
            }

            with self.subTest(suite_id=suite_id, manifest_id=manifest_id):
                self.assertEqual(
                    representative_text_models,
                    published_text_models,
                    msg=(
                        f"{suite_id} mixed-text manifest {manifest_id!r} "
                        "representative cases should cover both text models; "
                        f"expected {tuple(sorted(published_text_models))}, "
                        f"got {tuple(sorted(representative_text_models))}"
                    ),
                )

        self.assertNotEqual(
            mixed_text_manifest_ids,
            [],
            msg=f"{suite_id} should retain at least one mixed-text manifest",
        )

    def _assert_mixed_text_manifests_mirror_representative_bytes_rows(
        self,
        *,
        suite_id: str,
        expectation_table: object,
    ) -> None:
        manifests_by_id = {
            manifest.manifest_id: manifest
            for manifest in correctness.published_fixture_manifests()
        }
        mixed_text_manifest_ids: list[str] = []

        for manifest_id, manifest_expectation in expectation_table.items():
            manifest = manifests_by_id[manifest_id]
            text_models = {case.text_model for case in manifest.cases}
            if text_models != {"bytes", "str"}:
                continue

            mixed_text_manifest_ids.append(manifest_id)
            with self.subTest(suite_id=suite_id, manifest_id=manifest_id):
                representative_case_ids = manifest_expectation.representative_case_ids
                representative_str_case_ids = tuple(
                    case_id
                    for case_id in representative_case_ids
                    if case_id.endswith("-str")
                )
                representative_bytes_case_ids = tuple(
                    case_id
                    for case_id in representative_case_ids
                    if case_id.endswith("-bytes")
                )

                self.assertNotEqual(representative_str_case_ids, ())
                self.assertEqual(
                    representative_bytes_case_ids,
                    tuple(
                        f"{case_id.removesuffix('-str')}-bytes"
                        for case_id in representative_str_case_ids
                    ),
                )

        self.assertNotEqual(
            mixed_text_manifest_ids,
            [],
            msg=f"{suite_id} should retain at least one mixed-text manifest",
        )

    def test_suite_registry_reuses_canonical_expectation_tables(self) -> None:
        suites_by_id = {
            suite.suite_id: suite for suite in tracked_correctness_scorecard_suites()
        }

        self.assertEqual(set(suites_by_id), set(EXPECTED_SUITE_TABLES))

        for suite_id, expectation_table in EXPECTED_SUITE_TABLES.items():
            with self.subTest(suite_id=suite_id):
                suite = suites_by_id[suite_id]
                self.assertIs(suite.expectation_table, expectation_table)
                manifest_id = next(iter(expectation_table))
                self.assertNotIsInstance(expectation_table[manifest_id], dict)

    def test_suite_registry_target_manifests_follow_default_fixture_order(self) -> None:
        manifests = correctness.published_fixture_manifests()
        suite_ids: list[str] = []

        for suite in tracked_correctness_scorecard_suites():
            with self.subTest(suite_id=suite.suite_id):
                suite_ids.append(suite.suite_id)
                expected_target_manifest_ids = tuple(
                    manifest.manifest_id
                    for manifest in manifests
                    if manifest.manifest_id in suite.expectation_table
                )
                self.assertEqual(
                    correctness_scorecard_target_manifest_ids(suite.suite_id),
                    expected_target_manifest_ids,
                )
                self.assertNotEqual(expected_target_manifest_ids, ())

        self.assertEqual(len(suite_ids), len(set(suite_ids)))

    def test_unknown_suite_id_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            AssertionError,
            "unknown correctness scorecard suite 'missing-suite'; expected one of",
        ):
            correctness_scorecard_target_manifest_ids("missing-suite")

    def test_scorecard_case_rejects_manifests_outside_suite_expectations(self) -> None:
        target_manifest_id = correctness_scorecard_target_manifest_ids("combined")[0]
        self.assertNotIn(
            target_manifest_id,
            correctness_scorecard_target_manifest_ids("branch-local-backreference"),
        )

        with self.assertRaisesRegex(
            AssertionError,
            f"missing correctness expectation for '{target_manifest_id}'",
        ):
            correctness_scorecard_case("branch-local-backreference", target_manifest_id)

    def test_scorecard_cases_preserve_fixture_prefix_and_representative_case_order(
        self,
    ) -> None:
        manifests = correctness.published_fixture_manifests()
        fixture_manifest_ids = tuple(manifest.manifest_id for manifest in manifests)
        fixture_paths = tuple(
            str(manifest.path.relative_to(REPO_ROOT)) for manifest in manifests
        )

        for suite in tracked_correctness_scorecard_suites():
            for target_manifest_id in correctness_scorecard_target_manifest_ids(
                suite.suite_id
            ):
                with self.subTest(
                    suite_id=suite.suite_id,
                    manifest_id=target_manifest_id,
                ):
                    case = correctness_scorecard_case(suite.suite_id, target_manifest_id)
                    manifest_expectation = suite.expectation_table[target_manifest_id]
                    self.assertNotIsInstance(manifest_expectation, dict)
                    expected_representative_case_ids = (
                        manifest_expectation.representative_case_ids
                    )
                    target_index = fixture_manifest_ids.index(target_manifest_id)
                    expected_prefix_manifest_ids = fixture_manifest_ids[: target_index + 1]
                    expected_prefix_paths = fixture_paths[: target_index + 1]

                    self.assertEqual(case.target_manifest_id, target_manifest_id)
                    self.assertEqual(
                        case.expected_fixture_manifest_ids,
                        expected_prefix_manifest_ids,
                    )
                    self.assertEqual(case.expected_fixture_paths, expected_prefix_paths)
                    self.assertEqual(
                        tuple(
                            str(path.relative_to(REPO_ROOT)) for path in case.fixture_paths
                        ),
                        expected_prefix_paths,
                    )
                    self.assertEqual(
                        tuple(
                            fixture_case.case_id
                            for fixture_case in case.representative_cases
                        ),
                        expected_representative_case_ids,
                    )
                    self.assertEqual(
                        {fixture_case.manifest_id for fixture_case in case.representative_cases},
                        {target_manifest_id},
                    )

    def test_mixed_text_feature_scorecards_mirror_representative_bytes_rows(
        self,
    ) -> None:
        for suite_id, expectation_table in MIXED_TEXT_MIRROR_EXPECTATION_TABLES.items():
            self._assert_mixed_text_manifests_mirror_representative_bytes_rows(
                suite_id=suite_id,
                expectation_table=expectation_table,
            )

    def test_combined_scorecard_mixed_text_manifests_cover_both_representative_text_models(
        self,
    ) -> None:
        self._assert_mixed_text_manifests_cover_both_representative_text_models(
            suite_id="combined",
            expectation_table=COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
        )


if __name__ == "__main__":
    unittest.main()
