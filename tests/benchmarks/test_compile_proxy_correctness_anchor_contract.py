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


@cache
def _published_compile_case_signatures() -> frozenset[tuple[str | bytes, int, str]]:
    signatures: set[tuple[str | bytes, int, str]] = set()

    for fixture_path in DEFAULT_FIXTURE_PATHS:
        _, cases = load_fixture_manifest(fixture_path)
        for case in cases:
            if case.operation == "compile":
                signatures.add(_compile_case_signature(case))

    return frozenset(signatures)


def _unanchored_compile_workload_ids(manifest_path: pathlib.Path) -> tuple[str, ...]:
    _, workloads = load_manifest(manifest_path)
    compile_case_signatures = _published_compile_case_signatures()

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.operation in {"compile", "module.compile"}
        and _workload_signature(workload) not in compile_case_signatures
    )


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


if __name__ == "__main__":
    unittest.main()
