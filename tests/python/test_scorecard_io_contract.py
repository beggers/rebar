from __future__ import annotations

import json
import pathlib
import sys

import pytest

from rebar_harness import scorecard_io


def test_build_cpython_baseline_reports_current_interpreter_shape() -> None:
    baseline = scorecard_io.build_cpython_baseline(version_family="3.12.x")

    assert baseline["python_version_family"] == "3.12.x"
    assert baseline["python_implementation"].lower() == sys.implementation.name
    assert baseline["python_version"] == sys.version.split()[0]
    assert baseline["python_build"].keys() == {"name", "date"}
    assert isinstance(baseline["python_build"]["name"], str)
    assert isinstance(baseline["python_build"]["date"], str)
    assert isinstance(baseline["python_compiler"], str)
    assert isinstance(baseline["platform"], str)
    assert baseline["executable"] == sys.executable
    assert baseline["re_module"] == "re"


def test_format_python_scorecard_module_round_trips_through_python_loader(
    tmp_path: pathlib.Path,
) -> None:
    scorecard = {
        "schema_version": "1.0",
        "totals": {"cases": 3, "passed": 3},
        "manifests": [{"manifest_id": "fixture-pack", "count": 3}],
    }
    report_path = tmp_path / "latest.py"
    report_path.write_text(
        scorecard_io.format_python_scorecard_module(
            scorecard,
            report_attribute="REPORT",
        ),
        encoding="utf-8",
    )

    assert report_path.read_text(encoding="utf-8").startswith("REPORT = ")
    assert scorecard_io.load_python_dict_attribute(
        report_path,
        module_name_prefix="_scorecard_io_contract",
        attribute_name="REPORT",
        load_error_label="Python correctness scorecard",
        missing_error_label="Python correctness scorecard module",
        type_error_label="correctness scorecard",
    ) == scorecard


@pytest.mark.parametrize("suffix", (".py", ".json"))
def test_scorecard_report_round_trips_for_supported_extensions(
    tmp_path: pathlib.Path,
    suffix: str,
) -> None:
    scorecard = {
        "schema_version": "1.0",
        "environment": {"python": "3.12.3"},
        "totals": {"cases": 4, "passed": 4},
    }
    report_path = tmp_path / f"latest{suffix}"

    scorecard_io.write_scorecard_report(
        scorecard,
        report_path,
        report_attribute="REPORT",
        scorecard_kind="correctness",
    )

    if suffix == ".json":
        assert json.loads(report_path.read_text(encoding="utf-8")) == scorecard
    else:
        assert report_path.read_text(encoding="utf-8").startswith("REPORT = ")

    assert scorecard_io.load_scorecard_report(
        report_path,
        module_name_prefix="_scorecard_io_contract",
        report_attribute="REPORT",
        scorecard_kind="correctness",
    ) == scorecard


def test_scorecard_report_loaders_and_writers_reject_malformed_inputs(
    tmp_path: pathlib.Path,
) -> None:
    missing_attribute_path = tmp_path / "missing.py"
    missing_attribute_path.write_text("NOT_REPORT = {}\n", encoding="utf-8")
    wrong_type_python_path = tmp_path / "wrong_type.py"
    wrong_type_python_path.write_text("REPORT = []\n", encoding="utf-8")
    wrong_type_json_path = tmp_path / "wrong_type.json"
    wrong_type_json_path.write_text('["not-a-dict"]\n', encoding="utf-8")
    unsupported_input_path = tmp_path / "latest.txt"
    unsupported_input_path.write_text("REPORT = {}\n", encoding="utf-8")
    unsupported_output_path = tmp_path / "written.txt"

    with pytest.raises(ValueError) as missing_attribute_raised:
        scorecard_io.load_scorecard_report(
            missing_attribute_path,
            module_name_prefix="_scorecard_io_contract",
            report_attribute="REPORT",
            scorecard_kind="correctness",
        )
    assert str(missing_attribute_raised.value) == (
        f"Python correctness scorecard module {missing_attribute_path} is missing a REPORT value"
    )

    with pytest.raises(ValueError) as wrong_type_python_raised:
        scorecard_io.load_scorecard_report(
            wrong_type_python_path,
            module_name_prefix="_scorecard_io_contract",
            report_attribute="REPORT",
            scorecard_kind="correctness",
        )
    assert str(wrong_type_python_raised.value) == (
        f"correctness scorecard in {wrong_type_python_path} must be a dict"
    )

    with pytest.raises(ValueError) as wrong_type_json_raised:
        scorecard_io.load_scorecard_report(
            wrong_type_json_path,
            module_name_prefix="_scorecard_io_contract",
            report_attribute="REPORT",
            scorecard_kind="correctness",
        )
    assert str(wrong_type_json_raised.value) == (
        f"correctness scorecard in {wrong_type_json_path} must be a dict"
    )

    with pytest.raises(ValueError) as unsupported_input_raised:
        scorecard_io.load_scorecard_report(
            unsupported_input_path,
            module_name_prefix="_scorecard_io_contract",
            report_attribute="REPORT",
            scorecard_kind="correctness",
        )
    assert str(unsupported_input_raised.value) == (
        f"unsupported correctness scorecard extension '.txt' for {unsupported_input_path}"
    )

    with pytest.raises(ValueError) as unsupported_output_raised:
        scorecard_io.write_scorecard_report(
            {"schema_version": "1.0"},
            unsupported_output_path,
            report_attribute="REPORT",
            scorecard_kind="correctness",
        )
    assert str(unsupported_output_raised.value) == (
        f"unsupported correctness scorecard extension '.txt' for {unsupported_output_path}"
    )


def test_scorecard_report_descriptor_resolves_optional_paths_and_rejects_legacy_path(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports_root = tmp_path / "reports" / "correctness"
    reports_root.mkdir(parents=True)
    published_path = reports_root / "latest.py"
    legacy_path = reports_root / "latest.json"
    descriptor = scorecard_io.build_scorecard_report_descriptor(
        published_path=published_path,
        legacy_path=legacy_path,
        scorecard_kind="correctness",
    )

    monkeypatch.chdir(tmp_path)

    assert descriptor.report_attribute == "REPORT"
    assert descriptor.module_name_prefix == "_rebar_correctness_scorecard"
    assert descriptor.resolve_optional_path(None) is None
    assert descriptor.resolve_optional_path(pathlib.Path("reports/correctness/latest.py")) == (
        published_path.resolve()
    )

    with pytest.raises(ValueError) as legacy_path_raised:
        descriptor.resolve_optional_path(pathlib.Path("reports/correctness/latest.json"))
    assert str(legacy_path_raised.value) == (
        "reports/correctness/latest.json is a retired legacy published scorecard path; "
        "use reports/correctness/latest.py for the tracked published scorecard or a "
        "non-tracked temporary .json path for scratch output."
    )

    assert descriptor.validate_path(pathlib.Path("reports/correctness/latest.py")) == (
        published_path.resolve()
    )


def test_scorecard_report_descriptor_writes_resolved_reports_and_only_cleans_up_published_sidecar(
    tmp_path: pathlib.Path,
) -> None:
    reports_root = tmp_path / "reports" / "correctness"
    reports_root.mkdir(parents=True)
    published_path = reports_root / "latest.py"
    legacy_path = reports_root / "latest.json"
    scratch_path = tmp_path / "scratch-scorecard.json"
    descriptor = scorecard_io.build_scorecard_report_descriptor(
        published_path=published_path,
        legacy_path=legacy_path,
        scorecard_kind="correctness",
    )
    scorecard = {"schema_version": "1.0", "totals": {"cases": 2, "passed": 2}}

    legacy_path.write_text("{}\n", encoding="utf-8")
    descriptor.write_resolved_report(scorecard, scratch_path.resolve())

    assert scratch_path.is_file()
    assert descriptor.load(scratch_path) == scorecard
    assert legacy_path.is_file()

    descriptor.write_resolved_report(scorecard, published_path.resolve())

    assert descriptor.load(published_path) == scorecard
    assert not legacy_path.exists()
