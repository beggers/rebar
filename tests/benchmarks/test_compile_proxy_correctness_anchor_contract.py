from __future__ import annotations

from functools import cache
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"

from rebar_harness.benchmarks import load_manifest
from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifest


def _compile_case_signature(case) -> tuple[str | bytes, int, str]:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return (pattern, case.flags or 0, case.text_model)


def _workload_signature(workload) -> tuple[str | bytes, int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return (pattern, workload.flags, workload.text_model)


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


@cache
def _published_compile_case_signatures() -> frozenset[tuple[str | bytes, int, str]]:
    signatures: set[tuple[str | bytes, int, str]] = set()

    for fixture_path in DEFAULT_FIXTURE_PATHS:
        for case in load_fixture_manifest(fixture_path).cases:
            if case.operation == "compile":
                signatures.add(_compile_case_signature(case))

    return frozenset(signatures)


@cache
def _published_compile_case_ids_by_signature() -> dict[
    tuple[str | bytes, int, str], tuple[str, ...]
]:
    case_ids_by_signature: dict[tuple[str | bytes, int, str], list[str]] = {}

    for fixture_path in DEFAULT_FIXTURE_PATHS:
        for case in load_fixture_manifest(fixture_path).cases:
            if case.operation == "compile":
                signature = _compile_case_signature(case)
                case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(case_ids)
        for signature, case_ids in case_ids_by_signature.items()
    }


def _unanchored_compile_workload_ids(manifest_path: pathlib.Path) -> tuple[str, ...]:
    workloads = load_manifest(manifest_path).workloads
    compile_case_signatures = _published_compile_case_signatures()

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.operation in {"compile", "module.compile"}
        and _workload_signature(workload) not in compile_case_signatures
    )


def _anchored_compile_workload_case_ids(
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = load_manifest(manifest_path).workloads
    case_ids_by_signature = _published_compile_case_ids_by_signature()

    return {
        (manifest_path.name, workload.workload_id): case_ids_by_signature.get(
            _workload_signature(workload),
            (),
        )
        for workload in workloads
        if workload.operation in {"compile", "module.compile"}
    }


class CompileProxyCorrectnessAnchorContractTest(unittest.TestCase):
    def test_compile_matrix_compile_rows_stay_anchored_to_published_correctness_cases(
        self,
    ) -> None:
        self.assertEqual(
            _unanchored_compile_workload_ids(COMPILE_MATRIX_MANIFEST_PATH),
            (),
        )

    def test_regression_compile_rows_stay_anchored_to_published_correctness_cases(
        self,
    ) -> None:
        self.assertEqual(
            _unanchored_compile_workload_ids(REGRESSION_MATRIX_MANIFEST_PATH),
            (),
        )

    def test_compile_rows_stay_pinned_to_exact_published_correctness_case_ids(
        self,
    ) -> None:
        anchored_case_ids = {
            **_anchored_compile_workload_case_ids(COMPILE_MATRIX_MANIFEST_PATH),
            **_anchored_compile_workload_case_ids(REGRESSION_MATRIX_MANIFEST_PATH),
        }

        self.assertEqual(
            anchored_case_ids,
            EXPECTED_COMPILE_ANCHOR_CASE_IDS,
        )


if __name__ == "__main__":
    unittest.main()
