from __future__ import annotations

from typing import Any


def compile_proxy_correctness_case_signature(
    case: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if case.operation != "compile":
        return None
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return (
        "module.compile",
        pattern,
        (),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def compile_proxy_workload_signature(
    workload: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return (
        "module.compile",
        pattern,
        (),
        (),
        workload.flags,
        workload.text_model,
    )


def is_compile_proxy_workload(workload: Any) -> bool:
    return workload.operation in {"compile", "module.compile"}
