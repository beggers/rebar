from __future__ import annotations

from types import SimpleNamespace

from tests.benchmarks.compile_proxy_benchmark_anchor_support import (
    compile_proxy_correctness_case_signature,
    compile_proxy_signature,
    compile_proxy_workload_signature,
    is_compile_proxy_workload,
)


def _synthetic_case(
    *,
    operation: str,
    pattern: str | bytes | None,
    args: tuple[object, ...] = (),
    flags: int | None = None,
    text_model: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        operation=operation,
        pattern=pattern,
        args=args,
        flags=flags,
        text_model=text_model,
        pattern_payload=lambda: pattern,
    )


def _synthetic_workload(
    *,
    operation: str,
    pattern: str | bytes,
    flags: int,
    text_model: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        operation=operation,
        flags=flags,
        text_model=text_model,
        pattern_payload=lambda: pattern,
    )


def test_compile_proxy_signature_shape_matches_benchmark_contract() -> None:
    assert compile_proxy_signature("literal", flags=2, text_model="str") == (
        "module.compile",
        "literal",
        (),
        (),
        2,
        "str",
    )


def test_compile_proxy_correctness_case_signature_uses_compile_shape() -> None:
    case = _synthetic_case(
        operation="compile",
        pattern=None,
        args=(b"literal",),
        flags=None,
        text_model=None,
    )

    assert compile_proxy_correctness_case_signature(case) == (
        "module.compile",
        b"literal",
        (),
        (),
        0,
        "str",
    )


def test_compile_proxy_workload_signature_uses_compile_shape() -> None:
    workload = _synthetic_workload(
        operation="module.compile",
        pattern=b"literal",
        flags=8,
        text_model="bytes",
    )

    assert compile_proxy_workload_signature(workload) == (
        "module.compile",
        b"literal",
        (),
        (),
        8,
        "bytes",
    )


def test_is_compile_proxy_workload_includes_compile_operations_only() -> None:
    assert is_compile_proxy_workload(_synthetic_workload(
        operation="compile",
        pattern="literal",
        flags=0,
        text_model="str",
    ))
    assert is_compile_proxy_workload(_synthetic_workload(
        operation="module.compile",
        pattern="literal",
        flags=0,
        text_model="str",
    ))
    assert not is_compile_proxy_workload(_synthetic_workload(
        operation="module.search",
        pattern="literal",
        flags=0,
        text_model="str",
    ))
