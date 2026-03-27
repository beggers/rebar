from __future__ import annotations

import ast
from collections import Counter
from functools import cache
import inspect
import pathlib
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest import mock

import pytest

import tests.conftest as test_support
from tests.conftest import (
    REPO_ROOT,
    assert_declared_string_selector_registry_contract,
    assert_published_manifest_inventory_contract,
    assert_published_manifest_helper_contract,
    assert_published_manifest_helper_reload_contract,
    assert_published_selector_subset_paths_contract,
    completed_process,
    declared_string_constants_by_suffix,
    duplicate_items,
    duplicate_string_ids,
    fake_harness_cli_scorecard_result,
    manifest_records_by_id,
    records_by_string_id,
    report_path_from_cli_args,
    run_harness_cli,
    run_harness_scorecard,
)


COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"


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


def test_assert_declared_string_selector_registry_contract_accepts_aligned_unique_registry() -> None:
    module = ModuleType("aligned_selector_contract_module")
    module.DEFAULT_FIXTURE_SELECTOR = "default"
    module.PUBLISHED_FIXTURE_SELECTOR = "published"

    declared = assert_declared_string_selector_registry_contract(
        module,
        name_suffix="_FIXTURE_SELECTOR",
        selector_registry={
            "default": ("default_fixture.py",),
            "published": ("published_fixture.py",),
        },
    )

    assert tuple(declared.items()) == (
        ("DEFAULT_FIXTURE_SELECTOR", "default"),
        ("PUBLISHED_FIXTURE_SELECTOR", "published"),
    )


def test_assert_published_selector_subset_paths_contract_preserves_published_order(
    tmp_path: pathlib.Path,
) -> None:
    alpha_path = tmp_path / "alpha.py"
    beta_path = tmp_path / "beta.py"
    gamma_path = tmp_path / "gamma.py"

    for path in (alpha_path, beta_path, gamma_path):
        path.write_text("MANIFEST = {}\n", encoding="utf-8")

    published_paths = (gamma_path, alpha_path, beta_path)
    resolved_paths = (gamma_path, beta_path)

    assert_published_selector_subset_paths_contract(
        published_paths,
        resolved_paths,
        root_path=tmp_path,
        expected_filenames=("gamma.py", "beta.py"),
    )


def test_assert_published_selector_subset_paths_contract_accepts_implicit_filename_subset(
    tmp_path: pathlib.Path,
) -> None:
    alpha_path = tmp_path / "alpha.py"
    beta_path = tmp_path / "beta.py"
    gamma_path = tmp_path / "gamma.py"

    for path in (alpha_path, beta_path, gamma_path):
        path.write_text("MANIFEST = {}\n", encoding="utf-8")

    published_paths = (gamma_path, alpha_path, beta_path)

    assert_published_selector_subset_paths_contract(
        published_paths,
        (gamma_path, beta_path),
        root_path=tmp_path,
    )


def test_assert_published_selector_subset_paths_contract_rejects_duplicate_resolved_paths(
    tmp_path: pathlib.Path,
) -> None:
    alpha_path = tmp_path / "alpha.py"
    beta_path = tmp_path / "beta.py"

    for path in (alpha_path, beta_path):
        path.write_text("MANIFEST = {}\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        assert_published_selector_subset_paths_contract(
            (alpha_path, beta_path),
            (alpha_path, alpha_path),
            root_path=tmp_path,
        )


def test_assert_published_selector_subset_paths_contract_rejects_duplicate_expected_filenames(
    tmp_path: pathlib.Path,
) -> None:
    alpha_path = tmp_path / "alpha.py"
    beta_path = tmp_path / "beta.py"

    for path in (alpha_path, beta_path):
        path.write_text("MANIFEST = {}\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        assert_published_selector_subset_paths_contract(
            (alpha_path, beta_path),
            (alpha_path, beta_path),
            root_path=tmp_path,
            expected_filenames=("alpha.py", "alpha.py"),
        )


def test_assert_published_selector_subset_paths_contract_rejects_explicit_filename_order_drift(
    tmp_path: pathlib.Path,
) -> None:
    alpha_path = tmp_path / "alpha.py"
    beta_path = tmp_path / "beta.py"
    gamma_path = tmp_path / "gamma.py"

    for path in (alpha_path, beta_path, gamma_path):
        path.write_text("MANIFEST = {}\n", encoding="utf-8")

    with pytest.raises(AssertionError):
        assert_published_selector_subset_paths_contract(
            (gamma_path, alpha_path, beta_path),
            (beta_path, gamma_path),
            root_path=tmp_path,
            expected_filenames=("beta.py", "gamma.py"),
        )


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


def test_assert_published_manifest_inventory_contract_accepts_unique_manifest_and_child_ids(
) -> None:
    manifests = (
        SimpleNamespace(
            manifest_id="manifest-a",
            cases=(
                SimpleNamespace(case_id="case-a-1", manifest_id="manifest-a"),
                SimpleNamespace(case_id="case-a-2", manifest_id="manifest-a"),
            ),
        ),
        SimpleNamespace(
            manifest_id="manifest-b",
            cases=(SimpleNamespace(case_id="case-b-1", manifest_id="manifest-b"),),
        ),
    )

    cases = assert_published_manifest_inventory_contract(
        manifests,
        child_records="cases",
        child_id="case_id",
    )

    assert tuple(case.case_id for case in cases) == ("case-a-1", "case-a-2", "case-b-1")


def test_assert_published_manifest_inventory_contract_accepts_extra_manifest_uniqueness_fields(
) -> None:
    manifests = (
        SimpleNamespace(
            manifest_id="manifest-a",
            suite_id="suite-a",
            records=(SimpleNamespace(record_id="record-a", owner="manifest-a"),),
        ),
        SimpleNamespace(
            manifest_id="manifest-b",
            suite_id="suite-b",
            records=(SimpleNamespace(record_id="record-b", owner="manifest-b"),),
        ),
    )

    records = assert_published_manifest_inventory_contract(
        manifests,
        child_records=lambda manifest: manifest.records,
        child_id=lambda record: record.record_id,
        extra_manifest_unique_fields=("suite_id",),
        child_manifest_id=lambda record: record.owner,
    )

    assert tuple(record.record_id for record in records) == ("record-a", "record-b")


def test_assert_published_manifest_inventory_contract_rejects_duplicate_child_ids(
) -> None:
    manifests = (
        SimpleNamespace(
            manifest_id="manifest-a",
            cases=(SimpleNamespace(case_id="shared-case", manifest_id="manifest-a"),),
        ),
        SimpleNamespace(
            manifest_id="manifest-b",
            cases=(SimpleNamespace(case_id="shared-case", manifest_id="manifest-b"),),
        ),
    )

    with pytest.raises(AssertionError):
        assert_published_manifest_inventory_contract(
            manifests,
            child_records="cases",
            child_id="case_id",
        )


def test_assert_published_manifest_inventory_contract_rejects_manifests_without_children(
) -> None:
    manifests = (
        SimpleNamespace(
            manifest_id="manifest-a",
            cases=(SimpleNamespace(case_id="case-a-1", manifest_id="manifest-a"),),
        ),
        SimpleNamespace(manifest_id="manifest-b", cases=()),
    )

    with pytest.raises(AssertionError):
        assert_published_manifest_inventory_contract(
            manifests,
            child_records="cases",
            child_id="case_id",
        )


def test_assert_published_manifest_inventory_contract_rejects_children_owned_by_unknown_manifest(
) -> None:
    manifests = (
        SimpleNamespace(
            manifest_id="manifest-a",
            cases=(
                SimpleNamespace(case_id="case-a-1", manifest_id="manifest-a"),
                SimpleNamespace(case_id="orphan-case", manifest_id="missing-manifest"),
            ),
        ),
    )

    with pytest.raises(AssertionError):
        assert_published_manifest_inventory_contract(
            manifests,
            child_records="cases",
            child_id="case_id",
        )


def test_manifest_records_by_id_returns_original_records_keyed_by_manifest_id() -> None:
    manifest_a = SimpleNamespace(manifest_id="manifest-a", payload="alpha")
    manifest_b = SimpleNamespace(manifest_id="manifest-b", payload="beta")

    manifests_by_id = manifest_records_by_id(iter((manifest_a, manifest_b)))

    assert list(manifests_by_id) == ["manifest-a", "manifest-b"]
    assert manifests_by_id["manifest-a"] is manifest_a
    assert manifests_by_id["manifest-b"] is manifest_b


def test_records_by_string_id_returns_original_records_keyed_by_requested_id_in_input_order(
) -> None:
    case_a = SimpleNamespace(case_id="case-a", payload="alpha")
    case_b = SimpleNamespace(case_id="case-b", payload="beta")

    cases_by_id = records_by_string_id(
        iter((case_a, case_b)),
        id_attr="case_id",
    )

    assert list(cases_by_id) == ["case-a", "case-b"]
    assert cases_by_id["case-a"] is case_a
    assert cases_by_id["case-b"] is case_b


def test_records_by_string_id_rejects_duplicate_ids() -> None:
    duplicate_case_id = "duplicate-case"

    with pytest.raises(
        AssertionError,
        match=rf"duplicate ids: \['{duplicate_case_id}'\]",
    ):
        records_by_string_id(
            (
                SimpleNamespace(case_id=duplicate_case_id, payload="alpha"),
                SimpleNamespace(case_id=duplicate_case_id, payload="beta"),
            ),
            id_attr="case_id",
        )


def test_manifest_records_by_id_rejects_duplicate_manifest_ids() -> None:
    duplicate_manifest_id = "duplicate-manifest"

    with pytest.raises(
        AssertionError,
        match=rf"duplicate ids: \['{duplicate_manifest_id}'\]",
    ):
        manifest_records_by_id(
            (
                SimpleNamespace(manifest_id=duplicate_manifest_id, payload="alpha"),
                SimpleNamespace(manifest_id=duplicate_manifest_id, payload="beta"),
            )
        )


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


def test_fake_harness_cli_scorecard_result_writes_report_and_returns_json_summary() -> None:
    cli_args = ("--selector", "focused", "--report", str(REPO_ROOT / "scorecard.json"))

    with mock.patch.object(pathlib.Path, "write_text") as write_text_mock:
        observed = fake_harness_cli_scorecard_result(
            "custom.module",
            cli_args,
            summary={"passing_cases": 1},
            report_text='{"suite": "synthetic"}',
        )

    write_text_mock.assert_called_once_with('{"suite": "synthetic"}', encoding="utf-8")
    assert observed.args == ("python", "-m", "custom.module")
    assert observed.returncode == 0
    assert observed.stdout == '{"passing_cases": 1}'
    assert observed.stderr == ""


def test_report_path_from_cli_args_rejects_duplicate_report_flags() -> None:
    with pytest.raises(
        ValueError,
        match="cli args must include exactly one --report argument",
    ):
        report_path_from_cli_args(
            (
                "--selector",
                "focused",
                "--report",
                "first.json",
                "--report",
                "second.json",
            )
        )


def test_report_path_from_cli_args_rejects_missing_report_value() -> None:
    with pytest.raises(
        ValueError,
        match="--report must be followed by a path",
    ):
        report_path_from_cli_args(("--selector", "focused", "--report"))


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


def test_run_harness_scorecard_loads_python_correctness_reports_uses_owner_local_fixture_constant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract_fixture_path = (
        REPO_ROOT
        / "tests"
        / "conformance"
        / "fixtures"
        / "parser_matrix_contract_probe.py"
    )
    captured_call: dict[str, object] = {}

    def _run_harness_scorecard(
        module_name: str,
        cli_args: list[str],
        *,
        report_name: str,
    ) -> tuple[dict[str, int], dict[str, object]]:
        captured_call.update(
            {
                "module_name": module_name,
                "cli_args": list(cli_args),
                "report_name": report_name,
            }
        )
        summary = {"passing_cases": 1}
        return (
            summary,
            {
                "suite": "correctness",
                "fixtures": {
                    "path": str(contract_fixture_path.relative_to(REPO_ROOT)),
                    "manifest_id": "parser-matrix",
                },
                "summary": summary,
            },
        )

    monkeypatch.setattr(sys.modules[__name__], "run_harness_scorecard", _run_harness_scorecard)
    monkeypatch.setattr(
        sys.modules[__name__],
        "PARSER_FIXTURES_PATH",
        contract_fixture_path,
    )

    test_run_harness_scorecard_loads_python_correctness_reports()

    assert captured_call == {
        "module_name": "rebar_harness.correctness",
        "cli_args": ["--fixtures", str(contract_fixture_path)],
        "report_name": "parser-only.py",
    }


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


def test_run_harness_scorecard_loads_python_benchmark_reports_uses_owner_local_manifest_constant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract_manifest_path = (
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "compile_matrix_contract_probe.py"
    )
    captured_call: dict[str, object] = {}

    def _run_harness_scorecard(
        module_name: str,
        cli_args: list[str],
        *,
        report_name: str,
    ) -> tuple[dict[str, int], dict[str, object]]:
        captured_call.update(
            {
                "module_name": module_name,
                "cli_args": list(cli_args),
                "report_name": report_name,
            }
        )
        summary = {"measured_workloads": 1}
        return (
            summary,
            {
                "suite": "benchmarks",
                "artifacts": {
                    "manifest": str(contract_manifest_path.relative_to(REPO_ROOT)),
                    "manifest_id": "compile-matrix",
                },
                "summary": summary,
            },
        )

    monkeypatch.setattr(sys.modules[__name__], "run_harness_scorecard", _run_harness_scorecard)
    monkeypatch.setattr(
        sys.modules[__name__],
        "COMPILE_MATRIX_MANIFEST_PATH",
        contract_manifest_path,
    )

    test_run_harness_scorecard_loads_python_benchmark_reports()

    assert captured_call == {
        "module_name": "rebar_harness.benchmarks",
        "cli_args": ["--manifest", str(contract_manifest_path)],
        "report_name": "compile-matrix.py",
    }


def test_run_harness_scorecard_compile_manifest_path_constant_stays_owner_local() -> None:
    module_ast = ast.parse(inspect.getsource(sys.modules[__name__]))
    assigned_names = {
        target.id
        for node in module_ast.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    assert "COMPILE_MATRIX_MANIFEST_PATH" in assigned_names
    assert COMPILE_MATRIX_MANIFEST_PATH == (
        REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
    )
    assert COMPILE_MATRIX_MANIFEST_PATH.is_file()


def test_run_harness_scorecard_parser_fixture_path_constant_stays_owner_local() -> None:
    module_ast = ast.parse(inspect.getsource(sys.modules[__name__]))
    imported_parser_fixture_names = tuple(
        alias.asname or alias.name
        for node in module_ast.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "tests.conftest"
        for alias in node.names
        if alias.name == "PARSER_FIXTURES_PATH"
    )
    assigned_names = {
        target.id
        for node in module_ast.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    assert imported_parser_fixture_names == ()
    assert "PARSER_FIXTURES_PATH" in assigned_names
    assert PARSER_FIXTURES_PATH == (
        REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
    )
    assert PARSER_FIXTURES_PATH.is_file()


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


def test_run_harness_scorecard_rejects_preexisting_report_arg() -> None:
    with pytest.raises(
        ValueError,
        match="run_harness_scorecard manages its own --report argument",
    ):
        run_harness_scorecard(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(PARSER_FIXTURES_PATH),
                "--report",
                "preexisting.py",
            ],
            report_name="parser-only.py",
        )


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
        return fake_harness_cli_scorecard_result(
            module_name,
            cli_args,
            summary=expected_summary,
            report_text='{"suite": "synthetic", "summary": {"passing_cases": 1}}',
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
        return fake_harness_cli_scorecard_result(
            module_name,
            cli_args,
            summary=expected_summary,
            report_text=placeholder_payload,
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
        return fake_harness_cli_scorecard_result(
            module_name,
            cli_args,
            summary={"passing_cases": 1},
            report_text="REPORT = {'suite': 'synthetic'}\n",
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
        return fake_harness_cli_scorecard_result(
            module_name,
            cli_args,
            summary={"passing_cases": 1},
            report_text="REPORT = {'suite': 'synthetic'}\n",
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
