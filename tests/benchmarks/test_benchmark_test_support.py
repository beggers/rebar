from __future__ import annotations

from rebar_harness import benchmarks
from tests.benchmarks.benchmark_test_support import (
    _expected_exception_instance,
    _record_numeric_materialization_fields,
    _write_test_manifest,
)


def test_write_test_manifest_dedents_and_writes_utf8_text(tmp_path) -> None:
    manifest_path = _write_test_manifest(
        tmp_path,
        "sample_manifest.py",
        """\
            VALUE = "caf\u00e9"
        """,
    )

    assert manifest_path.read_text(encoding="utf-8") == 'VALUE = "caf\u00e9"\n'
    assert manifest_path.read_bytes() == 'VALUE = "caf\u00e9"\n'.encode("utf-8")


def test_expected_exception_instance_maps_supported_payloads() -> None:
    type_error = _expected_exception_instance(
        {
            "type": "TypeError",
            "message_substring": "type payload",
        }
    )
    value_error = _expected_exception_instance(
        {
            "type": "ValueError",
            "message_substring": "value payload",
        }
    )

    assert isinstance(type_error, TypeError)
    assert str(type_error) == "type payload"
    assert isinstance(value_error, ValueError)
    assert str(value_error) == "value payload"


def test_record_numeric_materialization_fields_collects_names_and_preserves_return_value(
    monkeypatch,
) -> None:
    original_materialize = benchmarks.materialize_numeric_workload_argument
    expected_value = original_materialize(
        {"type": "indexlike", "value": 7},
        field_name="kwargs.count",
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    observed_value = benchmarks.materialize_numeric_workload_argument(
        {"type": "indexlike", "value": 7},
        field_name="kwargs.count",
    )

    assert observed_field_names == ["kwargs.count"]
    assert type(observed_value) is type(expected_value)
    assert repr(observed_value) == repr(expected_value)
    assert observed_value.value == expected_value.value
