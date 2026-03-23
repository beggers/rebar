from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

import rebar
from tests.python import conftest as python_conftest


@dataclass(frozen=True)
class _BackendCase:
    unsupported_backends: tuple[str, ...] | None = ()
    unsupported_backend_reason: str | None = None


def _invoke_regex_backend(
    backend_param: str,
    *,
    parametrized_values: dict[str, object] | None = None,
) -> tuple[str, object]:
    node = SimpleNamespace()
    if parametrized_values is not None:
        node.callspec = SimpleNamespace(params=parametrized_values)
    request = SimpleNamespace(param=backend_param, node=node)
    return python_conftest.regex_backend.__wrapped__(request)


def test_regex_backend_returns_stdlib_backend_without_callspec_filters() -> None:
    backend_name, backend = _invoke_regex_backend("stdlib")

    assert backend_name == "stdlib"
    assert backend is python_conftest.re


def test_regex_backend_returns_rebar_backend_without_callspec_filters() -> None:
    backend_name, backend = _invoke_regex_backend("rebar")

    assert backend_name == "rebar"
    assert backend is rebar


def test_regex_backend_rejects_unknown_backend_parameter() -> None:
    with pytest.raises(
        AssertionError,
        match="unknown regex backend parameter 'missing-backend'",
    ):
        _invoke_regex_backend("missing-backend")


def test_regex_backend_skips_matching_unsupported_backend_with_explicit_reason() -> None:
    with pytest.raises(pytest.skip.Exception, match="bounded rebar gap"):
        _invoke_regex_backend(
            "rebar",
            parametrized_values={
                "case": _BackendCase(
                    unsupported_backends=("rebar",),
                    unsupported_backend_reason="bounded rebar gap",
                ),
            },
        )


def test_regex_backend_skips_matching_unsupported_backend_with_default_reason() -> None:
    with pytest.raises(
        pytest.skip.Exception,
        match="stdlib backend unsupported for this parity case",
    ):
        _invoke_regex_backend(
            "stdlib",
            parametrized_values={
                "case": _BackendCase(unsupported_backends=("stdlib",)),
            },
        )


def test_regex_backend_ignores_unsupported_backend_metadata_for_other_backends() -> None:
    backend_name, backend = _invoke_regex_backend(
        "stdlib",
        parametrized_values={
            "case": _BackendCase(
                unsupported_backends=("rebar",),
                unsupported_backend_reason="rebar-only gap",
            ),
        },
    )

    assert backend_name == "stdlib"
    assert backend is python_conftest.re


def test_regex_backend_treats_none_unsupported_backends_as_unfiltered() -> None:
    backend_name, backend = _invoke_regex_backend(
        "rebar",
        parametrized_values={
            "case": _BackendCase(
                unsupported_backends=None,
                unsupported_backend_reason="ignored metadata",
            ),
        },
    )

    assert backend_name == "rebar"
    assert backend is rebar


def test_regex_backend_rejects_multiple_param_values_disabling_same_backend() -> None:
    with pytest.raises(
        AssertionError,
        match="multiple parametrized values declare unsupported_backends for "
        "'rebar': \\('case', 'text'\\)",
    ):
        _invoke_regex_backend(
            "rebar",
            parametrized_values={
                "case": _BackendCase(
                    unsupported_backends=("rebar",),
                    unsupported_backend_reason="case gap",
                ),
                "text": _BackendCase(
                    unsupported_backends=("rebar",),
                    unsupported_backend_reason="text gap",
                ),
            },
        )


@pytest.mark.parametrize(
    ("backend_param", "expected_reason"),
    (
        pytest.param("stdlib", "stdlib-only fixture gap", id="stdlib"),
        pytest.param("rebar", "rebar-only fixture gap", id="rebar"),
    ),
)
def test_regex_backend_skips_only_for_matching_backend_when_param_values_target_different_backends(
    backend_param: str,
    expected_reason: str,
) -> None:
    with pytest.raises(pytest.skip.Exception, match=expected_reason):
        _invoke_regex_backend(
            backend_param,
            parametrized_values={
                "case": _BackendCase(
                    unsupported_backends=("stdlib",),
                    unsupported_backend_reason="stdlib-only fixture gap",
                ),
                "text": _BackendCase(
                    unsupported_backends=("rebar",),
                    unsupported_backend_reason="rebar-only fixture gap",
                ),
            },
        )


def test_regex_backend_falls_back_to_default_reason_for_falsey_matching_reason() -> None:
    with pytest.raises(
        pytest.skip.Exception,
        match="rebar backend unsupported for this parity case",
    ):
        _invoke_regex_backend(
            "rebar",
            parametrized_values={
                "case": _BackendCase(
                    unsupported_backends=("rebar",),
                    unsupported_backend_reason="",
                ),
            },
        )
