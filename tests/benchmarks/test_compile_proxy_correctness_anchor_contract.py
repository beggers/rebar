from __future__ import annotations

from functools import cache
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"

from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    published_case_ids_by_signature,
    unanchored_workload_ids,
)


def _compile_signature(
    pattern: str | bytes,
    *,
    flags: int,
    text_model: str,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    return ("module.compile", pattern, (), (), flags, text_model)


def _correctness_case_signature(case) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if case.operation != "compile":
        return None
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return _compile_signature(
        pattern,
        flags=case.flags or 0,
        text_model=case.text_model or "str",
    )


def _workload_signature(workload) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return _compile_signature(
        pattern,
        flags=workload.flags,
        text_model=workload.text_model,
    )


def _is_compile_workload(workload) -> bool:
    return workload.operation in {"compile", "module.compile"}


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
def _published_compile_case_ids_by_signature() -> dict[tuple[object, ...], tuple[str, ...]]:
    return published_case_ids_by_signature(_correctness_case_signature)


def _unanchored_compile_workload_ids(manifest_path: pathlib.Path) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=_published_compile_case_ids_by_signature(),
        workload_signature=_workload_signature,
        include_workload=_is_compile_workload,
    )


def _anchored_compile_workload_case_ids(
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=_published_compile_case_ids_by_signature(),
        workload_signature=_workload_signature,
        include_workload=_is_compile_workload,
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
