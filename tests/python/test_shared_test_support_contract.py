from __future__ import annotations

from collections import Counter
from functools import cache
import pathlib
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest import mock

import pytest

import tests.conftest as test_support
from tests.conftest import (
    REPO_ROOT,
    assert_published_manifest_helper_contract,
    assert_published_manifest_helper_reload_contract,
    completed_process,
    declared_string_constants_by_suffix,
    duplicate_items,
    duplicate_string_ids,
    report_path_from_cli_args,
    run_harness_cli,
    run_harness_scorecard,
)


PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"


def test_duplicate_items_returns_sorted_duplicate_keys_once() -> None:
    duplicates = duplicate_items(Counter({"beta": 2, "alpha": 3, "gamma": 1, "delta": 4}))

    assert duplicates == ["alpha", "beta", "delta"]


def test_duplicate_string_ids_accepts_one_shot_iterators() -> None:
    case_ids = iter(
        (
            "module-search-shared",
            "pattern-fullmatch-shared",
            "module-search-shared",
            "compile-shared",
            "compile-shared",
        )
    )

    assert duplicate_string_ids(case_ids) == (
        "compile-shared",
        "module-search-shared",
    )


def test_declared_string_constants_by_suffix_filters_only_matching_strings_in_order() -> None:
    module = ModuleType("selector_contract_module")
    module.PUBLIC_SURFACE_FIXTURE_SELECTOR = "public-surface"
    module.RELATED_FLAG = "ignored"
    module.PARSER_FIXTURE_SELECTOR = "parser"
    module.BENCHMARK_MANIFEST_SELECTOR = 7
    module.NON_STRING_SELECTOR = ["still-ignored"]
    module.PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR = "published-full-suite"

    declared = declared_string_constants_by_suffix(
        module,
        name_suffix="_FIXTURE_SELECTOR",
    )

    assert tuple(declared.items()) == (
        ("PUBLIC_SURFACE_FIXTURE_SELECTOR", "public-surface"),
        ("PARSER_FIXTURE_SELECTOR", "parser"),
        ("PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR", "published-full-suite"),
    )


def test_declared_string_constants_by_suffix_returns_empty_dict_without_matching_strings() -> None:
    module = ModuleType("empty_selector_contract_module")
    module.UNRELATED = "value"
    module.NON_STRING_SELECTOR = 3

    assert declared_string_constants_by_suffix(module, name_suffix="_SELECTOR") == {}


def test_assert_published_manifest_helper_contract_checks_cache_order_and_post_clear_reload(
    tmp_path: pathlib.Path,
) -> None:
    first_path = tmp_path / "manifest_a.py"
    second_path = tmp_path / "manifest_b.py"
    current_paths = [first_path, second_path]
    loader_calls: list[tuple[pathlib.Path, ...]] = []

    def _load_current_manifests() -> tuple[SimpleNamespace, ...]:
        paths = tuple(current_paths)
        loader_calls.append(paths)
        return tuple(
            SimpleNamespace(path=path, manifest_id=path.stem)
            for path in paths
        )

    @cache
    def published_manifests() -> tuple[SimpleNamespace, ...]:
        return _load_current_manifests()

    manifests = assert_published_manifest_helper_contract(
        published_manifests,
        expected_paths=(first_path, second_path),
        expected_manifest_ids=("manifest_a", "manifest_b"),
    )

    assert loader_calls == [(first_path, second_path)]

    current_paths[:] = [second_path, first_path]
    loader_calls.clear()
    reloaded_manifests = assert_published_manifest_helper_reload_contract(
        published_manifests,
        clear_cache=published_manifests.cache_clear,
        expected_paths=(second_path, first_path),
        expected_manifest_ids=("manifest_b", "manifest_a"),
        observed_load_calls=loader_calls,
    )

    assert reloaded_manifests is not manifests


def test_run_harness_cli_uses_repo_local_pythonpath_and_check_by_default() -> None:
    expected_result = completed_process("python", "-m", "custom.module")

    with mock.patch.object(
        test_support.subprocess,
        "run",
        return_value=expected_result,
    ) as run_mock:
        observed = run_harness_cli(
            "custom.module",
            ["--selector", "focused"],
        )

    assert observed is expected_result
    run_mock.assert_called_once_with(
        [sys.executable, "-m", "custom.module", "--selector", "focused"],
        check=True,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(test_support.PYTHON_SOURCE)},
        capture_output=True,
        text=True,
    )


def test_run_harness_cli_can_disable_check_without_changing_invocation_shape() -> None:
    expected_result = completed_process(
        "python",
        "-m",
        "custom.module",
        returncode=2,
        stderr="usage error",
    )

    with mock.patch.object(
        test_support.subprocess,
        "run",
        return_value=expected_result,
    ) as run_mock:
        observed = run_harness_cli(
            "custom.module",
            ["--selector", "focused"],
            check=False,
        )

    assert observed is expected_result
    run_mock.assert_called_once_with(
        [sys.executable, "-m", "custom.module", "--selector", "focused"],
        check=False,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(test_support.PYTHON_SOURCE)},
        capture_output=True,
        text=True,
    )


def test_run_harness_cli_accepts_one_shot_cli_arg_iterators() -> None:
    expected_result = completed_process("python", "-m", "custom.module")
    cli_args = iter(("--selector", "focused", "--limit", "3"))

    with mock.patch.object(
        test_support.subprocess,
        "run",
        return_value=expected_result,
    ) as run_mock:
        observed = run_harness_cli(
            "custom.module",
            cli_args,
        )

    assert observed is expected_result
    run_mock.assert_called_once_with(
        [sys.executable, "-m", "custom.module", "--selector", "focused", "--limit", "3"],
        check=True,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(test_support.PYTHON_SOURCE)},
        capture_output=True,
        text=True,
    )


def test_run_harness_scorecard_loads_python_correctness_reports() -> None:
    summary, scorecard = run_harness_scorecard(
        "rebar_harness.correctness",
        [
            "--fixtures",
            str(PARSER_FIXTURES_PATH),
        ],
        report_name="parser-only.py",
    )

    assert scorecard["suite"] == "correctness"
    assert scorecard["fixtures"]["path"] == str(PARSER_FIXTURES_PATH.relative_to(REPO_ROOT))
    assert scorecard["fixtures"]["manifest_id"] == "parser-matrix"
    assert scorecard["summary"] == summary


def test_run_harness_scorecard_loads_python_benchmark_reports() -> None:
    summary, scorecard = run_harness_scorecard(
        "rebar_harness.benchmarks",
        [
            "--manifest",
            str(COMPILE_MATRIX_MANIFEST_PATH),
        ],
        report_name="compile-matrix.py",
    )

    assert scorecard["suite"] == "benchmarks"
    assert scorecard["artifacts"]["manifest"] == str(
        COMPILE_MATRIX_MANIFEST_PATH.relative_to(REPO_ROOT)
    )
    assert scorecard["artifacts"]["manifest_id"] == "compile-matrix"
    assert {key: scorecard["summary"][key] for key in summary} == summary


def test_run_harness_scorecard_accepts_one_shot_cli_arg_iterators() -> None:
    summary, scorecard = run_harness_scorecard(
        "rebar_harness.correctness",
        iter(
            (
                "--fixtures",
                str(PARSER_FIXTURES_PATH),
            )
        ),
        report_name="parser-only.py",
    )

    assert scorecard["suite"] == "correctness"
    assert scorecard["fixtures"]["path"] == str(PARSER_FIXTURES_PATH.relative_to(REPO_ROOT))
    assert scorecard["fixtures"]["manifest_id"] == "parser-matrix"
    assert scorecard["summary"] == summary


def test_run_harness_scorecard_loads_json_reports_without_importing_module_loader() -> None:
    expected_summary = {"passing_cases": 1}
    expected_scorecard = {"suite": "synthetic", "summary": expected_summary}

    def _run_harness_cli(
        module_name: str,
        cli_args: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        assert module_name == "custom.module"
        assert check is True
        report_path = report_path_from_cli_args(cli_args)
        report_path.write_text(
            '{"suite": "synthetic", "summary": {"passing_cases": 1}}',
            encoding="utf-8",
        )
        return completed_process(
            "python",
            "-m",
            module_name,
            stdout='{"passing_cases": 1}\n',
        )

    with mock.patch.object(
        test_support,
        "run_harness_cli",
        side_effect=_run_harness_cli,
    ) as run_mock, mock.patch.object(
        test_support.importlib,
        "import_module",
        side_effect=AssertionError("json reports should not import scorecard modules"),
    ) as import_module_mock:
        summary, scorecard = run_harness_scorecard(
            "custom.module",
            ["--selector", "focused"],
            report_name="scorecard.json",
        )

    assert summary == expected_summary
    assert scorecard == expected_scorecard
    run_mock.assert_called_once()
    import_module_mock.assert_not_called()


def test_run_harness_scorecard_uses_non_json_scorecard_loader_when_available() -> None:
    expected_summary = {"passing_cases": 1}
    expected_scorecard = {"suite": "synthetic", "summary": expected_summary}
    placeholder_payload = "synthetic python scorecard payload"

    def _run_harness_cli(
        module_name: str,
        cli_args: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        assert module_name == "custom.module"
        assert check is True
        report_path = report_path_from_cli_args(cli_args)
        report_path.write_text(placeholder_payload, encoding="utf-8")
        return completed_process(
            "python",
            "-m",
            module_name,
            stdout='{"passing_cases": 1}\n',
        )

    def _load_scorecard(report_path: pathlib.Path) -> dict[str, object]:
        assert report_path.name == "scorecard.py"
        assert report_path.read_text(encoding="utf-8") == placeholder_payload
        return expected_scorecard

    load_scorecard_mock = mock.Mock(side_effect=_load_scorecard)
    module = ModuleType("custom.module")
    module.SCORECARD_REPORT = SimpleNamespace(load=load_scorecard_mock)

    with mock.patch.object(
        test_support,
        "run_harness_cli",
        side_effect=_run_harness_cli,
    ) as run_mock, mock.patch.object(
        test_support.importlib,
        "import_module",
        return_value=module,
    ) as import_module_mock:
        summary, scorecard = run_harness_scorecard(
            "custom.module",
            ["--selector", "focused"],
            report_name="scorecard.py",
        )

    assert summary == expected_summary
    assert scorecard == expected_scorecard
    run_mock.assert_called_once()
    import_module_mock.assert_called_once_with("custom.module")
    load_scorecard_mock.assert_called_once()
    (report_path,) = load_scorecard_mock.call_args.args
    assert report_path.name == "scorecard.py"


def test_run_harness_scorecard_wraps_non_json_import_failures_in_value_error() -> None:
    def _run_harness_cli(
        module_name: str,
        cli_args: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        assert module_name == "custom.module"
        assert check is True
        report_path_from_cli_args(cli_args)
        return completed_process(
            "python",
            "-m",
            module_name,
            stdout='{"passing_cases": 1}\n',
        )

    with mock.patch.object(
        test_support,
        "run_harness_cli",
        side_effect=_run_harness_cli,
    ), mock.patch.object(
        test_support.importlib,
        "import_module",
        side_effect=ImportError("no such module"),
    ):
        with pytest.raises(
            ValueError,
            match=(
                "run_harness_scorecard cannot load a non-JSON report for "
                "'custom.module'"
            ),
        ) as exc_info:
            run_harness_scorecard(
                "custom.module",
                ["--selector", "focused"],
                report_name="scorecard.py",
            )

    assert isinstance(exc_info.value.__cause__, ImportError)
    assert str(exc_info.value.__cause__) == "no such module"


def test_run_harness_scorecard_wraps_missing_non_json_loader_in_value_error() -> None:
    def _run_harness_cli(
        module_name: str,
        cli_args: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        assert module_name == "custom.module"
        assert check is True
        report_path_from_cli_args(cli_args)
        return completed_process(
            "python",
            "-m",
            module_name,
            stdout='{"passing_cases": 1}\n',
        )

    module = ModuleType("custom.module")

    with mock.patch.object(
        test_support,
        "run_harness_cli",
        side_effect=_run_harness_cli,
    ), mock.patch.object(
        test_support.importlib,
        "import_module",
        return_value=module,
    ):
        with pytest.raises(
            ValueError,
            match=(
                "run_harness_scorecard cannot load a non-JSON report for "
                "'custom.module'"
            ),
        ) as exc_info:
            run_harness_scorecard(
                "custom.module",
                ["--selector", "focused"],
                report_name="scorecard.py",
            )

    assert isinstance(exc_info.value.__cause__, AttributeError)
    cause_message = str(exc_info.value.__cause__)
    assert "custom.module" in cause_message
    assert "SCORECARD_REPORT" in cause_message
