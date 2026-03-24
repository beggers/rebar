from __future__ import annotations

import pathlib
import re

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    Workload,
    load_manifest,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import _write_test_manifest
from tests.benchmarks.compiled_pattern_module_compile_benchmark_support import (
    _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    CompiledPatternModuleCompileContractCase,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_manifest,
)
from tests.benchmarks.wrong_text_model_benchmark_owner_support import (
    _PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC,
    _assert_wrong_text_model_payload_round_trip,
)


def _render_manifest_inline_value(value: object) -> str:
    if isinstance(value, re.RegexFlag):
        if value == re.NOFLAG:
            return "re.NOFLAG"
        return f"re.RegexFlag({int(value)})"
    return repr(value)


def _manifest_kwargs_source(kwargs_payload: dict[str, object] | None) -> tuple[str, str]:
    if kwargs_payload is None:
        return "", ""

    rendered_items = ", ".join(
        f"{key!r}: {_render_manifest_inline_value(value)}"
        for key, value in kwargs_payload.items()
    )
    manifest_imports = (
        "import re\n\n"
        if any(isinstance(value, re.RegexFlag) for value in kwargs_payload.values())
        else ""
    )
    return manifest_imports, "{" + rendered_items + "}"


COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS = tuple(
    owner_spec.contract_case()
    for owner_spec in _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS
)


def test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-nested-constant-contract",
        "defaults": {
            "warmup_iterations": 2,
            "sample_iterations": 3,
            "timed_samples": 4,
            "text_model": "bytes",
        },
        "workloads": [
            {
                "id": "module-sub-callable-nested-constant-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"(abc)",
                "text_model": "bytes",
                "replacement": {
                    "type": "callable_constant",
                    "value": {
                        "literal": "literal",
                        "sequence": [
                            "inner",
                            {
                                "type": "bytes",
                                "value": "XYZ",
                                "encoding": "ascii",
                            },
                            {"nested": "value"},
                        ],
                    },
                },
                "haystack": "abc",
                "categories": ["replacement", "callable", "constant", "bytes"],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_nested_constant_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-nested-constant-contract"
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-nested-constant-contract-bytes",
    ]

    workload = workloads[0]
    assert workload.text_model == "bytes"
    assert workload_to_payload(workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "literal": "literal",
            "sequence": [
                "inner",
                {
                    "type": "bytes",
                    "value": "XYZ",
                    "encoding": "ascii",
                },
                {"nested": "value"},
            ],
        },
    }

    replacement = workload.replacement_payload()
    assert callable(replacement)
    assert replacement.__module__ == "rebar_harness.benchmarks"
    assert replacement.__qualname__ == "callable_constant"

    raw_replacement = workload.replacement
    assert isinstance(raw_replacement, dict)
    raw_value = raw_replacement["value"]
    assert isinstance(raw_value, dict)
    raw_sequence = raw_value["sequence"]
    assert isinstance(raw_sequence, list)
    raw_bytes_descriptor = raw_sequence[1]
    assert isinstance(raw_bytes_descriptor, dict)
    raw_nested_mapping = raw_sequence[2]
    assert isinstance(raw_nested_mapping, dict)

    raw_value["literal"] = "mutated"
    raw_sequence[0] = "changed"
    raw_bytes_descriptor["value"] = "CHANGED"
    raw_nested_mapping["nested"] = "changed"

    match = re.search(workload.pattern_payload(), workload.haystack_payload())
    assert match is not None
    assert replacement(match) == {
        "literal": b"literal",
        "sequence": [
            b"inner",
            b"XYZ",
            {"nested": b"value"},
        ],
    }


def test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-text-model-contract",
        "workloads": [
            {
                "id": "module-sub-callable-invalid-text-model",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": {
                    "type": "callable_constant",
                    "value": "CONST",
                },
                "haystack": "abc",
                "text_model": "utf-16",
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_text_model_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    with pytest.raises(ValueError, match=r"unsupported text model 'utf-16'"):
        workloads[0].replacement_payload()


def test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values(
    tmp_path: pathlib.Path,
) -> None:
    invalid_modules = (
        (
            "missing_manifest.py",
            "WORKLOADS = []",
            r"is missing a MANIFEST value",
        ),
        (
            "non_dict_manifest.py",
            "MANIFEST = ['not-a-dict']",
            r"must be a dict",
        ),
    )

    for filename, source, error_pattern in invalid_modules:
        manifest_path = _write_test_manifest(tmp_path, filename, source)
        with pytest.raises(ValueError, match=error_pattern):
            load_manifest(manifest_path)


def test_benchmark_workload_value_normalization_recursively_preserves_literals_and_stringifies_mapping_keys(
) -> None:
    assert benchmarks.normalize_workload_value(
        {
            1: [
                {"flag": True, 2: None},
                3,
            ],
            False: {
                "message": "ok",
                4: 1.5,
            },
        }
    ) == {
        "1": [
            {"flag": True, "2": None},
            3,
        ],
        "False": {
            "message": "ok",
            "4": 1.5,
        },
    }


def test_benchmark_workload_value_normalization_rejects_non_literal_containers() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("unsupported workload value ('unexpected',)"),
    ):
        benchmarks.normalize_workload_value(("unexpected",))


@pytest.mark.parametrize(
    (
        "manifest_id",
        "kwargs_payload",
        "expected_exception",
        "pattern",
        "flags",
        "text_model",
        "error_pattern",
    ),
    (
        pytest.param(
            "collection-replacement-boundary",
            None,
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads are only supported on the "
                "`module-boundary` manifest"
            ),
            id="manifest-scope",
        ),
        pytest.param(
            "module-boundary",
            {"flags": re.NOFLAG},
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `flags=0`, `flags=False`, and "
                "`flags=IGNORECASE` rejection keyword carriers"
            ),
            id="keyword-carrier-noflag-scope",
        ),
        pytest.param(
            "module-boundary",
            {"flags": True},
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `flags=0`, `flags=False`, and "
                "`flags=IGNORECASE` rejection keyword carriers"
            ),
            id="keyword-carrier-scope",
        ),
        pytest.param(
            "module-boundary",
            {"flags": int(re.IGNORECASE)},
            None,
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `flags=0`, `flags=False`, and "
                "`flags=IGNORECASE` rejection keyword carriers"
            ),
            id="ignorecase-rejection-missing-expected-exception",
        ),
        pytest.param(
            "module-boundary",
            None,
            {
                "type": "TypeError",
                "message_substring": "bad pattern",
            },
            "abc",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "successful same-text-model literal or named-group rows or "
                "the bounded `flags=IGNORECASE` rejection rows"
            ),
            id="expected-exception-not-supported",
        ),
        pytest.param(
            "module-boundary",
            None,
            None,
            "(?:abc)",
            0,
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            ),
            id="pattern-scope",
        ),
        pytest.param(
            "module-boundary",
            None,
            None,
            "abc",
            int(re.IGNORECASE),
            "str",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            ),
            id="flags-scope",
        ),
        pytest.param(
            "module-boundary",
            None,
            None,
            "abc",
            0,
            "unicode",
            re.escape(
                "benchmark compiled-pattern module-helper "
                "module.compile workloads currently only support "
                "the bounded `abc` str/bytes literal success pair, "
                "the exact same-text-model `(?P<word>abc)` str/bytes "
                "named-group success pair, and `flags=IGNORECASE` "
                "rejection pairs"
            ),
            id="text-model-scope",
        ),
    ),
)
def test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    kwargs_payload: dict[str, object] | None,
    expected_exception: dict[str, str] | None,
    pattern: str,
    flags: int,
    text_model: str,
    error_pattern: str,
) -> None:
    manifest_imports, rendered_kwargs_payload = _manifest_kwargs_source(kwargs_payload)
    kwargs_line = (
        f'                "kwargs": {rendered_kwargs_payload},\n'
        if kwargs_payload is not None
        else ""
    )
    manifest_source = f"""{manifest_imports}MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "module-compile-invalid-compiled-pattern-contract",
                "bucket": "module-compile",
                "family": "module",
                "operation": "module.compile",
                "pattern": {pattern!r},
                "expected_exception": {expected_exception!r},
                "flags": {flags!r},
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
{kwargs_line}                "text_model": {text_model!r},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_compiled_pattern_module_compile_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    payload = {
        "manifest_id": manifest_id,
        "workload_id": "module-compile-invalid-compiled-pattern-contract",
        "bucket": "module-compile",
        "family": "module",
        "operation": "module.compile",
        "pattern": pattern,
        "expected_exception": expected_exception,
        "flags": flags,
        "use_compiled_pattern": True,
        "count": 0,
        "maxsplit": 0,
        "text_model": text_model,
        "cache_mode": "warm",
        "timing_scope": "module-helper-call",
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": False,
    }
    if kwargs_payload is not None:
        payload["kwargs"] = kwargs_payload

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(payload)


@pytest.mark.parametrize(
    ("case_group", "source_workload"),
    tuple(
        pytest.param(case_group, source_workload, id=source_workload.workload_id)
        for case_group in COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS
        for source_workload in case_group.source_workloads()
        if source_workload.expected_exception
    ),
)
def test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows(
    tmp_path: pathlib.Path,
    case_group: CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> None:
    manifest = _source_tree_contract_manifest(
        (source_workload,),
        spec=case_group.contract_builder_spec(),
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_ignorecase_validation_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    case_group.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )


@pytest.mark.parametrize(
    (
        "manifest_id",
        "operation",
        "cache_mode",
        "error_pattern",
    ),
    (
        pytest.param(
            "collection-replacement-boundary",
            "pattern.search",
            "warm",
            (
                re.escape(
                    "benchmark compiled-pattern module-helper workloads currently "
                    "only support"
                )
                + r".*"
                + re.escape("; got 'pattern.search'")
            ),
            id="operation-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.findall",
            "cold",
            re.escape(
                "benchmark compiled-pattern module-helper workloads currently require "
                "`cache_mode` to be `warm` or `purged` so timed callbacks exclude "
                "pattern compilation"
            ),
            id="collection-replacement-cache-mode",
        ),
        pytest.param(
            "module-boundary",
            "module.search",
            "cold",
            re.escape(
                "benchmark compiled-pattern module-helper workloads currently require "
                "`cache_mode` to be `warm` or `purged` so timed callbacks exclude "
                "pattern compilation"
            ),
            id="module-boundary-cache-mode",
        ),
    ),
)
def test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    operation: str,
    cache_mode: str,
    error_pattern: str,
) -> None:
    family = operation.split(".", 1)[0]
    bucket = operation.replace(".", "-")

    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "compiled-pattern-invalid-workload-contract",
                "bucket": {bucket!r},
                "family": {family!r},
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": None,
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "text_model": "str",
                "cache_mode": {cache_mode!r},
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_compiled_pattern_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": manifest_id,
                "workload_id": "compiled-pattern-invalid-workload-contract",
                "bucket": bucket,
                "family": family,
                "operation": operation,
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": None,
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "text_model": "str",
                "cache_mode": cache_mode,
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


@pytest.mark.parametrize(
    ("raw_expected_exception", "expected_normalized"),
    (
        pytest.param(
            {"type": 404},
            {"type": "404"},
            id="type-only",
        ),
        pytest.param(
            {"type": "TypeError", "message_substring": 17},
            {"type": "TypeError", "message_substring": "17"},
            id="type-and-message",
        ),
    ),
)
def test_benchmark_expected_exception_normalization_stringifies_scalar_fields(
    raw_expected_exception: dict[str, object],
    expected_normalized: dict[str, str],
) -> None:
    assert (
        benchmarks.normalize_expected_exception(raw_expected_exception)
        == expected_normalized
    )


@pytest.mark.parametrize(
    ("invalid_expected_exception", "error_pattern"),
    (
        pytest.param(
            ["TypeError"],
            "benchmark workload expected_exception must be an object",
            id="non-object",
        ),
        pytest.param(
            {"message_substring": "NoneType"},
            r"benchmark workload expected_exception requires a `type`",
            id="missing-type",
        ),
        pytest.param(
            {"type": "TypeError", "detail": "extra"},
            re.escape(
                "benchmark workload expected_exception contains unsupported keys: "
                "['detail']"
            ),
            id="unsupported-key",
        ),
        pytest.param(
            {"type": "TypeError", "message_substring": ("NoneType",)},
            "unsupported workload value",
            id="unsupported-nested-value",
        ),
    ),
)
def test_standard_benchmark_expected_exception_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    invalid_expected_exception: object,
    error_pattern: str,
) -> None:
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-expected-exception-contract",
        "workloads": [
            {{
                "id": "module-sub-invalid-expected-exception-contract",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": "x",
                "haystack": "abc",
                "expected_exception": {invalid_expected_exception!r},
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_expected_exception_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": "python-benchmark-invalid-expected-exception-contract",
                "workload_id": "module-sub-invalid-expected-exception-contract",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "haystack": "abc",
                "replacement": "x",
                "expected_exception": invalid_expected_exception,
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC.source_workloads()
    ),
)
def test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio(
    tmp_path: pathlib.Path,
    source_workload: Workload,
) -> None:
    owner_spec = _PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC
    manifest = _source_tree_contract_manifest(
        (source_workload,),
        spec=owner_spec.contract_builder_spec(),
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        f"python_benchmark_{source_workload.workload_id}_haystack_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    loaded_workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(loaded_workload)
    round_tripped = workload_from_payload(payload)

    _assert_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
        use_compiled_pattern=owner_spec.use_compiled_pattern,
        timing_scope=owner_spec.timing_scope,
    )
    assert loaded_workload.workload_id == f"{source_workload.workload_id}-contract"


@pytest.mark.parametrize(
    (
        "manifest_id",
        "operation",
        "use_compiled_pattern",
        "pos",
        "endpos",
        "kwargs_payload",
        "text_model",
        "haystack_text_model",
        "expected_exception",
        "error_pattern",
    ),
    (
        pytest.param(
            "python-benchmark-invalid-haystack-text-model-contract",
            "module.sub",
            True,
            None,
            None,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model is only supported on the "
                "`collection-replacement-boundary` manifest and the bounded "
                "`module-boundary` compiled-pattern wrong-text-model trio plus the "
                "bounded `pattern-boundary` direct Pattern search/match/fullmatch trio"
            ),
            id="manifest-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.search",
            False,
            None,
            None,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "compiled-pattern module.split/module.findall/module.finditer/"
                "module.sub/module.subn workloads"
            ),
            id="operation-scope",
        ),
        pytest.param(
            "module-boundary",
            "module.sub",
            True,
            None,
            None,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "compiled-pattern module.search/module.match/module.fullmatch "
                "workloads on the `module-boundary` manifest"
            ),
            id="module-boundary-operation-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.sub",
            True,
            None,
            None,
            {},
            "str",
            "str",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model must differ from the "
                "workload text_model"
            ),
            id="same-text-model",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.sub",
            True,
            None,
            None,
            {},
            "str",
            "bytes",
            None,
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "timed TypeError rows"
            ),
            id="missing-expected-exception",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.sub",
            True,
            None,
            None,
            {},
            "str",
            "utf-16",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model must be `str` or `bytes`; "
                "got 'utf-16'"
            ),
            id="invalid-override-model",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "pattern.findall",
            False,
            None,
            None,
            {},
            "bytes",
            "str",
            {
                "type": "TypeError",
                "message_substring": "cannot use a bytes pattern on a string-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.split()/Pattern.sub()/Pattern.subn() positional "
                "helper workloads"
            ),
            id="pattern-operation-scope",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "pattern.split",
            False,
            None,
            None,
            {"maxsplit": 1},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.split()/Pattern.sub()/Pattern.subn() positional "
                "helper workloads"
            ),
            id="pattern-keyword-carrier-not-supported",
        ),
        pytest.param(
            "pattern-boundary",
            "pattern.findall",
            False,
            None,
            None,
            {},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.search()/Pattern.match()/Pattern.fullmatch() "
                "positional helper workloads on the `pattern-boundary` manifest"
            ),
            id="pattern-boundary-operation-scope",
        ),
        pytest.param(
            "pattern-boundary",
            "pattern.search",
            False,
            None,
            None,
            {"pos": 1},
            "str",
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.search()/Pattern.match()/Pattern.fullmatch() "
                "positional helper workloads on the `pattern-boundary` manifest"
            ),
            id="pattern-boundary-keyword-carrier-not-supported",
        ),
        pytest.param(
            "pattern-boundary",
            "pattern.match",
            False,
            1,
            None,
            {},
            "bytes",
            "str",
            {
                "type": "TypeError",
                "message_substring": "cannot use a bytes pattern on a string-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "direct Pattern.search()/Pattern.match()/Pattern.fullmatch() "
                "positional helper workloads on the `pattern-boundary` manifest"
            ),
            id="pattern-boundary-window-carrier-not-supported",
        ),
        pytest.param(
            "pattern-boundary",
            "pattern.fullmatch",
            False,
            None,
            None,
            {},
            "str",
            "str",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark workload haystack_text_model must differ from the "
                "workload text_model"
            ),
            id="pattern-boundary-same-text-model",
        ),
        pytest.param(
            "pattern-boundary",
            "pattern.fullmatch",
            False,
            None,
            None,
            {},
            "str",
            "bytes",
            {
                "type": "ValueError",
                "message_substring": "boom",
            },
            re.escape(
                "benchmark workload haystack_text_model currently only supports "
                "timed TypeError rows"
            ),
            id="pattern-boundary-non-type-error",
        ),
    ),
)
def test_standard_benchmark_haystack_text_model_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    operation: str,
    use_compiled_pattern: bool,
    pos: object,
    endpos: object,
    kwargs_payload: dict[str, object],
    text_model: str,
    haystack_text_model: str,
    expected_exception: dict[str, str] | None,
    error_pattern: str,
) -> None:
    bucket = operation.replace(".", "-")
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "module-sub-invalid-haystack-text-model-contract",
                "bucket": {bucket!r},
                "family": "module",
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "abc",
                "replacement": "x",
                "expected_exception": {expected_exception!r},
                "flags": 0,
                "use_compiled_pattern": {use_compiled_pattern!r},
                "count": 1,
                "maxsplit": 0,
                "pos": {pos!r},
                "endpos": {endpos!r},
                "kwargs": {kwargs_payload!r},
                "text_model": {text_model!r},
                "haystack_text_model": {haystack_text_model!r},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_haystack_text_model_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": manifest_id,
                "workload_id": "module-sub-invalid-haystack-text-model-contract",
                "bucket": bucket,
                "family": "module",
                "operation": operation,
                "pattern": "abc",
                "haystack": "abc",
                "replacement": "x",
                "expected_exception": expected_exception,
                "flags": 0,
                "use_compiled_pattern": use_compiled_pattern,
                "count": 1,
                "maxsplit": 0,
                "pos": pos,
                "endpos": endpos,
                "kwargs": kwargs_payload,
                "text_model": text_model,
                "haystack_text_model": haystack_text_model,
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )


@pytest.mark.parametrize(
    (
        "manifest_id",
        "operation",
        "kwargs_payload",
        "haystack_text_model",
        "expected_exception",
        "error_pattern",
    ),
    (
        pytest.param(
            "module-boundary",
            "module.search",
            {},
            None,
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads currently only support "
                "successful same-text-model rows or timed wrong-text-model "
                "TypeError rows"
            ),
            id="unexpected-exception-on-success-row",
        ),
        pytest.param(
            "collection-replacement-boundary",
            "module.search",
            {},
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads are only supported on the "
                "`module-boundary` manifest"
            ),
            id="module-boundary-manifest-scope",
        ),
        pytest.param(
            "module-boundary",
            "module.search",
            {"flags": 0},
            "bytes",
            {
                "type": "TypeError",
                "message_substring": "cannot use a string pattern on a bytes-like object",
            },
            re.escape(
                "benchmark compiled-pattern module-helper "
                "search/match/fullmatch workloads currently only support "
                "positional helper calls"
            ),
            id="keyword-carrier-not-supported",
        ),
    ),
)
def test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    manifest_id: str,
    operation: str,
    kwargs_payload: dict[str, object],
    haystack_text_model: str | None,
    expected_exception: dict[str, str] | None,
    error_pattern: str,
) -> None:
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": {manifest_id!r},
        "workloads": [
            {{
                "id": "module-search-invalid-compiled-pattern-boundary-contract",
                "bucket": "module-search",
                "family": "module",
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": {expected_exception!r},
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {kwargs_payload!r},
                "text_model": "str",
                "haystack_text_model": {haystack_text_model!r},
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_compiled_pattern_module_boundary_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": manifest_id,
                "workload_id": "module-search-invalid-compiled-pattern-boundary-contract",
                "bucket": "module-search",
                "family": "module",
                "operation": operation,
                "pattern": "abc",
                "haystack": "abc",
                "expected_exception": expected_exception,
                "flags": 0,
                "use_compiled_pattern": True,
                "count": 0,
                "maxsplit": 0,
                "kwargs": kwargs_payload,
                "text_model": "str",
                "haystack_text_model": haystack_text_model,
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            }
        )
