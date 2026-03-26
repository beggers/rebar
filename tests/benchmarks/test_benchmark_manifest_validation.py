from __future__ import annotations

import pathlib
import re

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    Workload,
    load_manifest,
    load_manifests,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import benchmark_test_support
from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support


def _validation_payload(**overrides: object) -> dict[str, object]:
    return {
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": False,
        **overrides,
    }


def _assert_manifest_and_payload_entry_points_raise(
    *,
    tmp_path: pathlib.Path,
    filename: str,
    manifest_source: str,
    payload: dict[str, object],
    error_pattern: str,
) -> None:
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        filename,
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(payload)

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

    manifest_path = benchmark_test_support._write_test_manifest(
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


def test_standard_benchmark_manifest_materializes_callable_replacement_descriptors(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-loader-contract",
        "defaults": {
            "warmup_iterations": 2,
            "sample_iterations": 3,
            "timed_samples": 4,
            "text_model": "str",
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
        },
        "workloads": [
            {
                "id": "module-sub-callable-numbered-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((bc)+)d",
                "replacement": {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "haystack": "zzabcbcdzz",
                "count": 0,
                "categories": ["replacement", "callable", "numbered-group", "str"],
                "notes": [
                    "Ensures Python-backed benchmark manifests materialize numbered callable replacement descriptors."
                ],
            },
            {
                "id": "pattern-subn-callable-named-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                "replacement": {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "haystack": "zzabcbcdabcbcdzz",
                "count": 1,
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "categories": ["replacement", "callable", "named-group", "str"],
                "notes": [
                    "Ensures Python-backed benchmark manifests materialize named callable replacement descriptors."
                ],
            },
            {
                "id": "module-sub-callable-constant-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((bc)+)d",
                "replacement": {
                    "type": "callable_constant",
                    "value": {
                        "type": "bytes",
                        "value": "CONST",
                        "encoding": "ascii",
                    },
                },
                "haystack": "zzabcbcdzz",
                "text_model": "bytes",
                "categories": ["replacement", "callable", "constant", "bytes"],
                "notes": [
                    "Ensures Python-backed benchmark manifests keep bytes-aware callable constants available for subprocess serialization and runtime materialization."
                ],
            },
        ],
    }
    """

    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_loader_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-loader-contract"
    assert not hasattr(manifest, "defaults")
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-numbered-contract-str",
        "pattern-subn-callable-named-contract-str",
        "module-sub-callable-constant-contract-bytes",
    ]

    numbered_workload = workloads[0]
    assert numbered_workload.warmup_iterations == 2
    assert numbered_workload.sample_iterations == 3
    assert numbered_workload.timed_samples == 4
    assert numbered_workload.pattern_payload() == r"a((bc)+)d"
    assert numbered_workload.haystack_payload() == "zzabcbcdzz"
    numbered_replacement = numbered_workload.replacement_payload()
    assert callable(numbered_replacement)
    assert numbered_replacement.__module__ == "rebar_harness.benchmarks"
    assert numbered_replacement.__qualname__ == "callable_match_group"
    numbered_match = re.search(
        numbered_workload.pattern_payload(),
        numbered_workload.haystack_payload(),
    )
    assert numbered_match is not None
    assert numbered_replacement(numbered_match) == "bcbcx"
    assert workload_to_payload(numbered_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x",
    }

    named_workload = workloads[1]
    assert named_workload.cache_mode == "purged"
    assert named_workload.timing_scope == "pattern-helper-call"
    named_replacement = named_workload.replacement_payload()
    assert callable(named_replacement)
    assert named_replacement.__module__ == "rebar_harness.benchmarks"
    assert named_replacement.__qualname__ == "callable_match_group"
    named_match = re.search(
        named_workload.pattern_payload(),
        named_workload.haystack_payload(),
    )
    assert named_match is not None
    assert named_replacement(named_match) == "<bc>"
    assert workload_to_payload(named_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": "inner",
        "prefix": "<",
        "suffix": ">",
    }

    constant_bytes_workload = workloads[2]
    assert constant_bytes_workload.text_model == "bytes"
    assert constant_bytes_workload.pattern_payload() == rb"a((bc)+)d"
    assert constant_bytes_workload.haystack_payload() == b"zzabcbcdzz"
    constant_bytes_replacement = constant_bytes_workload.replacement_payload()
    assert callable(constant_bytes_replacement)
    assert constant_bytes_replacement.__module__ == "rebar_harness.benchmarks"
    assert constant_bytes_replacement.__qualname__ == "callable_constant"
    constant_bytes_match = re.search(
        constant_bytes_workload.pattern_payload(),
        constant_bytes_workload.haystack_payload(),
    )
    assert constant_bytes_match is not None
    assert constant_bytes_replacement(constant_bytes_match) == b"CONST"
    assert workload_to_payload(constant_bytes_workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "type": "bytes",
            "value": "CONST",
            "encoding": "ascii",
        },
    }


def test_standard_benchmark_manifest_loader_rejects_duplicate_ids(
    tmp_path: pathlib.Path,
) -> None:
    duplicate_modules = (
        (
            (
                "duplicate_benchmark_manifest_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-a",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_benchmark_manifest_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-b",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark manifest id .*duplicate-benchmark-manifest-id",
        ),
        (
            (
                "duplicate_benchmark_workload_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-a",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_benchmark_workload_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-b",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark workload id .*duplicate-benchmark-workload-id",
        ),
    )

    for first_module, second_module, error_pattern in duplicate_modules:
        first_path = benchmark_test_support._write_test_manifest(
            tmp_path,
            *first_module,
        )
        second_path = benchmark_test_support._write_test_manifest(
            tmp_path,
            *second_module,
        )
        with pytest.raises(ValueError, match=error_pattern):
            load_manifests([first_path, second_path])


def test_standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-bytes-template-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "module-sub-template-numbered-conditional-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((b|c){2,})\\2(?(2)d|e)",
                "replacement": r"\\1x",
                "haystack": "abbbd",
                "text_model": "bytes",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "categories": [
                    "replacement",
                    "template",
                    "numbered-group",
                    "bytes",
                ],
                "notes": [
                    "Ensures bytes benchmark manifests materialize numbered template replacements through the same published nested-group helper path."
                ],
            },
            {
                "id": "pattern-subn-template-named-conditional-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                "replacement": r"\\g<inner>x",
                "haystack": "zzacccdabcbccdzz",
                "count": 1,
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "categories": [
                    "replacement",
                    "template",
                    "named-group",
                    "bytes",
                ],
                "notes": [
                    "Ensures bytes benchmark manifests materialize named template replacements through the same published nested-group helper path."
                ],
            },
        ],
    }
    """

    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_bytes_template_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-bytes-template-contract"
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-template-numbered-conditional-contract-bytes",
        "pattern-subn-template-named-conditional-contract-bytes",
    ]

    numbered_workload = workloads[0]
    assert numbered_workload.text_model == "bytes"
    assert numbered_workload.pattern_payload() == rb"a((b|c){2,})\2(?(2)d|e)"
    assert numbered_workload.haystack_payload() == b"abbbd"
    assert numbered_workload.replacement_payload() == b"\\1x"
    assert workload_to_payload(numbered_workload)["replacement"] == "\\1x"

    named_workload = workloads[1]
    assert named_workload.text_model == "bytes"
    assert named_workload.pattern_payload() == (
        rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"
    )
    assert named_workload.haystack_payload() == b"zzacccdabcbccdzz"
    assert named_workload.replacement_payload() == b"\\g<inner>x"
    assert workload_to_payload(named_workload)["replacement"] == "\\g<inner>x"

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

    manifest_path = benchmark_test_support._write_test_manifest(
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
        manifest_path = benchmark_test_support._write_test_manifest(
            tmp_path,
            filename,
            source,
        )
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
    rendered_kwargs_payload = ""
    manifest_imports = ""
    if kwargs_payload is not None:
        rendered_items = []
        for key, value in kwargs_payload.items():
            if isinstance(value, re.RegexFlag):
                rendered_value = (
                    "re.NOFLAG" if value == re.NOFLAG else f"re.RegexFlag({int(value)})"
                )
                manifest_imports = "import re\n\n"
            else:
                rendered_value = repr(value)
            rendered_items.append(f"{key!r}: {rendered_value}")
        rendered_kwargs_payload = "{" + ", ".join(rendered_items) + "}"
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

    payload = _validation_payload(
        manifest_id=manifest_id,
        workload_id="module-compile-invalid-compiled-pattern-contract",
        bucket="module-compile",
        family="module",
        operation="module.compile",
        pattern=pattern,
        expected_exception=expected_exception,
        flags=flags,
        use_compiled_pattern=True,
        count=0,
        maxsplit=0,
        text_model=text_model,
        cache_mode="warm",
        timing_scope="module-helper-call",
    )
    if kwargs_payload is not None:
        payload["kwargs"] = kwargs_payload

    _assert_manifest_and_payload_entry_points_raise(
        tmp_path=tmp_path,
        filename="python_benchmark_invalid_compiled_pattern_module_compile_contract.py",
        manifest_source=manifest_source,
        payload=payload,
        error_pattern=error_pattern,
    )


@pytest.mark.parametrize(
    ("case_group", "source_workload"),
    tuple(
        pytest.param(case_group, source_workload, id=source_workload.workload_id)
        for case_group in source_tree_support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        for source_workload in case_group.source_workloads()
        if source_workload.expected_exception
    ),
)
def test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows(
    tmp_path: pathlib.Path,
    case_group: benchmark_test_support.CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> None:
    manifest = benchmark_test_support._source_tree_contract_manifest(
        (source_workload,),
        spec=case_group.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
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
    "contract_case",
    source_tree_support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
    ids=lambda contract_case: contract_case.case_id,
)
def test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    contract_case: benchmark_test_support.CompiledPatternModuleCompileContractCase,
) -> None:
    source_workloads = contract_case.source_workloads()
    manifest = benchmark_test_support._source_tree_contract_manifest(
        source_workloads,
        spec=contract_case.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        contract_case.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        contract_case.expected_source_workload_ids()
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        workload_id for workload_id, _case_id in contract_case.expected_anchor_pairs
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        contract_case.assert_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        if source_workload.expected_exception is None:
            benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                round_tripped,
                contract_case.run_cpython_workload(workload),
            )
            continue

        expected_exception = benchmark_test_support._expected_exception_instance(
            source_workload.expected_exception
        )
        with pytest.raises(
            type(expected_exception),
            match=source_workload.expected_exception["message_substring"],
        ) as expected_error:
            contract_case.run_cpython_workload(workload)
        with pytest.raises(type(expected_error.value)) as observed_error:
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
        assert str(observed_error.value) == str(expected_error.value)


def test_standard_benchmark_compiled_pattern_module_compile_keyword_payload_round_trip_preserves_keyword_signature_type(
    tmp_path: pathlib.Path,
) -> None:
    contract_case = next(
        case
        for case in source_tree_support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "bool-false"
    )
    source_workload = contract_case.source_workloads()[0]
    manifest = benchmark_test_support._source_tree_contract_manifest(
        (source_workload,),
        spec=contract_case.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_keyword_type_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_case.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert source_workload.kwargs == {"flags": False}
    assert contract_case.keyword_signature == (("flags", "bool", False),)
    assert type(payload["kwargs"]["flags"]) is bool
    assert type(round_tripped.kwargs["flags"]) is bool


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in source_tree_support._compiled_pattern_wrong_text_model_specs()
    ),
)
def test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    spec: dict[str, object],
) -> None:
    source_workloads = (
        source_tree_support._compiled_pattern_wrong_text_model_source_workloads(spec)
    )
    manifest = benchmark_test_support._source_tree_contract_manifest(
        source_workloads,
        spec=benchmark_test_support._COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS[
            str(spec["contract_manifest_id"])
        ],
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        str(spec["contract_filename"]),
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(load_manifest(manifest_path).workloads)

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        spec["expected_source_workload_ids"]
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract" for workload_id in spec["expected_source_workload_ids"]
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [True] * len(
        source_workloads
    )
    assert [workload.timing_scope for workload in workloads] == [
        "module-helper-call"
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        benchmark_test_support._assert_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            benchmark_test_support._run_cpython_compiled_pattern_module_helper_workload(
                workload,
                collection_replacement_callback_flags=0,
            )
        with pytest.raises(TypeError) as observed_error:
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "owner_spec",
    source_tree_support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
    ids=lambda owner_spec: owner_spec.case_id,
)
def test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    owner_spec: object,
) -> None:
    source_workloads = owner_spec.source_workloads()
    manifest = benchmark_test_support._source_tree_contract_manifest(
        source_workloads,
        spec=owner_spec.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        owner_spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        owner_spec.expected_source_workload_ids
    )
    assert all(
        benchmark_test_support.include_live_compiled_pattern_module_success_workload(
            workload
        )
        for workload in source_workloads
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        benchmark_test_support._assert_compiled_pattern_module_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            owner_spec=owner_spec,
        )
        benchmark_test_support.assert_benchmark_workload_matches_expected_result(
            round_tripped,
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped),
        )


@pytest.mark.parametrize(
    "contract_surface",
    source_tree_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS,
    ids=lambda contract_surface: contract_surface.case_id,
)
def test_standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    contract_surface: object,
) -> None:
    source_workloads = contract_surface.source_workloads()
    manifest = benchmark_test_support._source_tree_contract_manifest(
        source_workloads,
        spec=contract_surface.spec.contract_builder_spec(),
    )

    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        contract_surface.spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        contract_surface.spec.expected_source_workload_ids
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        contract_surface.assert_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        contract_surface.assert_outcome(
            source_workload,
            workload,
            round_tripped,
        )


def test_compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements(
) -> None:
    success_surface = next(
        surface
        for surface in (
            source_tree_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "success"
    )
    keyword_error_surface = next(
        surface
        for surface in (
            source_tree_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "keyword-error"
    )

    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id
        == "module-sub-count-bool-false-keyword-warm-str-compiled-pattern"
    )
    success_workload = benchmark_test_support._source_tree_contract_workload(
        success_source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    success_payload = workload_to_payload(success_workload)
    success_round_tripped = workload_from_payload(success_payload)

    success_surface.assert_payload_round_trip(
        success_source_workload,
        success_payload,
        success_round_tripped,
    )
    assert success_payload.get("expected_exception") is None
    assert success_round_tripped.expected_exception is None
    assert type(success_payload["kwargs"]["count"]) is bool
    assert type(success_round_tripped.kwargs["count"]) is bool

    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern"
    )
    keyword_error_workload = benchmark_test_support._source_tree_contract_workload(
        keyword_error_source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    keyword_error_payload = workload_to_payload(keyword_error_workload)
    keyword_error_round_tripped = workload_from_payload(keyword_error_payload)

    keyword_error_surface.assert_payload_round_trip(
        keyword_error_source_workload,
        keyword_error_payload,
        keyword_error_round_tripped,
    )
    assert (
        keyword_error_payload["expected_exception"]
        == keyword_error_source_workload.expected_exception
    )
    assert (
        keyword_error_round_tripped.expected_exception
        == keyword_error_source_workload.expected_exception
    )

    split_duplicate_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern"
    )
    sub_keyword_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-sub-count-keyword-warm-str-compiled-pattern"
    )

    assert keyword_error_surface.spec.expected_materialized_field_names(
        split_duplicate_workload
    ) == ("maxsplit", "kwargs.maxsplit")
    assert success_surface.spec.expected_materialized_field_names(
        sub_keyword_workload
    ) == ("kwargs.count",)

    assert {
        (
            workload.workload_id,
            workload.operation,
            workload.text_model,
            workload.kwargs["count"],
            benchmark_test_support.run_benchmark_workload_with_cpython(workload),
        )
        for workload in (
            source_tree_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        )
        if workload.operation in {"module.sub", "module.subn"}
        and type(workload.kwargs.get("count")) is bool
    } == {
        (
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            True,
            "xabc",
        ),
        (
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            False,
            "xx",
        ),
        (
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            False,
            (b"xx", 2),
        ),
        (
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            True,
            (b"xabc", 1),
        ),
    }


def test_compiled_pattern_module_helper_keyword_contract_rows_preserve_cpython_outcomes_across_success_and_error_lanes(
) -> None:
    success_surface = next(
        surface
        for surface in (
            source_tree_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "success"
    )
    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id
        == "module-subn-count-keyword-purged-bytes-compiled-pattern"
    )
    success_workload = benchmark_test_support._source_tree_contract_workload(
        success_source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    success_payload = workload_to_payload(success_workload)
    success_round_tripped = workload_from_payload(success_payload)

    success_surface.assert_outcome(
        success_source_workload,
        success_workload,
        success_round_tripped,
    )
    assert success_surface.run_cpython_helper_workload(success_workload) == (
        b"xabc",
        1,
    )

    keyword_error_surface = next(
        surface
        for surface in (
            source_tree_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "keyword-error"
    )
    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-subn-count-alias-keyword-purged-bytes-compiled-pattern"
    )
    keyword_error_workload = benchmark_test_support._source_tree_contract_workload(
        keyword_error_source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    keyword_error_payload = workload_to_payload(keyword_error_workload)
    keyword_error_round_tripped = workload_from_payload(keyword_error_payload)

    keyword_error_surface.assert_outcome(
        keyword_error_source_workload,
        keyword_error_workload,
        keyword_error_round_tripped,
    )
    with pytest.raises(TypeError):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            keyword_error_round_tripped
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

    _assert_manifest_and_payload_entry_points_raise(
        tmp_path=tmp_path,
        filename="python_benchmark_invalid_compiled_pattern_contract.py",
        manifest_source=manifest_source,
        payload=_validation_payload(
            manifest_id=manifest_id,
            workload_id="compiled-pattern-invalid-workload-contract",
            bucket=bucket,
            family=family,
            operation=operation,
            pattern="abc",
            haystack="abc",
            expected_exception=None,
            flags=0,
            use_compiled_pattern=True,
            count=0,
            maxsplit=0,
            text_model="str",
            cache_mode=cache_mode,
            timing_scope="module-helper-call",
        ),
        error_pattern=error_pattern,
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

    _assert_manifest_and_payload_entry_points_raise(
        tmp_path=tmp_path,
        filename="python_benchmark_invalid_expected_exception_contract.py",
        manifest_source=manifest_source,
        payload=_validation_payload(
            manifest_id="python-benchmark-invalid-expected-exception-contract",
            workload_id="module-sub-invalid-expected-exception-contract",
            bucket="module-sub",
            family="module",
            operation="module.sub",
            pattern="abc",
            haystack="abc",
            replacement="x",
            expected_exception=invalid_expected_exception,
            flags=0,
            count=0,
            maxsplit=0,
            text_model="str",
            cache_mode="warm",
            timing_scope="module-helper-call",
        ),
        error_pattern=error_pattern,
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in benchmark_test_support.selected_manifest_workloads(
            BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py",
            include_workload=benchmark_test_support._is_pattern_boundary_wrong_text_model_workload,
        )
    ),
)
def test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio(
    tmp_path: pathlib.Path,
    source_workload: Workload,
) -> None:
    manifest = benchmark_test_support._source_tree_contract_manifest(
        (source_workload,),
        spec=benchmark_test_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        f"python_benchmark_{source_workload.workload_id}_haystack_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    loaded_workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(loaded_workload)
    round_tripped = workload_from_payload(payload)

    benchmark_test_support.assert_pattern_helper_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
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

    _assert_manifest_and_payload_entry_points_raise(
        tmp_path=tmp_path,
        filename="python_benchmark_invalid_haystack_text_model_contract.py",
        manifest_source=manifest_source,
        payload=_validation_payload(
            manifest_id=manifest_id,
            workload_id="module-sub-invalid-haystack-text-model-contract",
            bucket=bucket,
            family="module",
            operation=operation,
            pattern="abc",
            haystack="abc",
            replacement="x",
            expected_exception=expected_exception,
            flags=0,
            use_compiled_pattern=use_compiled_pattern,
            count=1,
            maxsplit=0,
            pos=pos,
            endpos=endpos,
            kwargs=kwargs_payload,
            text_model=text_model,
            haystack_text_model=haystack_text_model,
            cache_mode="warm",
            timing_scope="module-helper-call",
        ),
        error_pattern=error_pattern,
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

    _assert_manifest_and_payload_entry_points_raise(
        tmp_path=tmp_path,
        filename="python_benchmark_invalid_compiled_pattern_module_boundary_contract.py",
        manifest_source=manifest_source,
        payload=_validation_payload(
            manifest_id=manifest_id,
            workload_id="module-search-invalid-compiled-pattern-boundary-contract",
            bucket="module-search",
            family="module",
            operation=operation,
            pattern="abc",
            haystack="abc",
            expected_exception=expected_exception,
            flags=0,
            use_compiled_pattern=True,
            count=0,
            maxsplit=0,
            kwargs=kwargs_payload,
            text_model="str",
            haystack_text_model=haystack_text_model,
            cache_mode="warm",
            timing_scope="module-helper-call",
        ),
        error_pattern=error_pattern,
    )
