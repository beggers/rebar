from __future__ import annotations

import re
import warnings

from rebar_harness.correctness import (
    _normalize_value,
    build_observation_summary,
    compare_observations,
    normalize_exception,
    normalize_match_metadata,
    normalize_warning_records,
)


def test_normalize_match_metadata_preserves_bytes_named_capture_shape() -> None:
    match = re.search(rb"(?P<outer>(ab)?)(?P<inner>c)", b"zabc")

    assert match is not None
    assert normalize_match_metadata(match) == {
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
    }


def test_normalize_match_metadata_keeps_missing_optional_named_group_details() -> None:
    match = re.fullmatch(r"(?P<word>a)?b", "b")

    assert match is not None
    assert normalize_match_metadata(match) == {
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
    }


def test_normalize_value_exhausts_iterators_and_normalizes_nested_bytes() -> None:
    iterator = iter([b"ab", {"x": (1, b"y")}])

    assert _normalize_value(iterator) == {
        "items": [
            {"encoding": "latin-1", "value": "ab"},
            {"x": [1, {"encoding": "latin-1", "value": "y"}]},
        ],
        "exhausted": True,
    }
    assert next(iterator, None) is None


def test_normalize_warning_and_exception_payloads_preserve_diagnostic_details() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warnings.warn("alpha", RuntimeWarning)
        warnings.warn("beta", FutureWarning)

    warning_payload = normalize_warning_records(caught)
    assert warning_payload == [
        {"category": "RuntimeWarning", "message": "alpha"},
        {"category": "FutureWarning", "message": "beta"},
    ]

    try:
        re.compile("(")
    except re.error as exc:
        exception_payload = normalize_exception(exc)
    else:  # pragma: no cover - stdlib compile must raise here.
        raise AssertionError("expected re.compile('(') to raise")

    assert exception_payload["type"] == "error"
    assert "missing )" in exception_payload["message"]
    assert exception_payload["pos"] == 0
    assert exception_payload["lineno"] == 1
    assert exception_payload["colno"] == 1


def test_compare_observations_prefers_unimplemented_result() -> None:
    comparison, mismatch_notes = compare_observations(
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

    assert comparison == "unimplemented"
    assert mismatch_notes == ["rebar adapter reports support as unimplemented"]


def test_compare_observations_reports_each_payload_mismatch_in_stable_order() -> None:
    comparison, mismatch_notes = compare_observations(
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

    assert comparison == "fail"
    assert mismatch_notes == [
        "outcome mismatch: success != exception",
        "warning payload mismatch",
        "result payload mismatch",
        "exception payload mismatch",
    ]


def test_build_observation_summary_counts_sorted_outcomes_warnings_and_exceptions() -> None:
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

    assert build_observation_summary(observations) == {
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
    }
