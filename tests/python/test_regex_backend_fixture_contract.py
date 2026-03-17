from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from tests.python.conftest import _unsupported_backend_skip_reason


@dataclass(frozen=True)
class FakeParityCase:
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


def _request_with_params(**params: object) -> object:
    return SimpleNamespace(node=SimpleNamespace(callspec=SimpleNamespace(params=params)))


def test_unsupported_backend_skip_reason_ignores_requests_without_callspec() -> None:
    request = SimpleNamespace(node=SimpleNamespace())

    assert _unsupported_backend_skip_reason(request, "rebar") is None


def test_unsupported_backend_skip_reason_preserves_case_param_compatibility() -> None:
    request = _request_with_params(
        case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="case-style reason",
        )
    )

    assert _unsupported_backend_skip_reason(request, "rebar") == "case-style reason"


def test_unsupported_backend_skip_reason_supports_nonstandard_case_param_names() -> None:
    request = _request_with_params(
        supplemental_case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="supplemental reason",
        )
    )

    assert (
        _unsupported_backend_skip_reason(request, "rebar") == "supplemental reason"
    )


def test_unsupported_backend_skip_reason_ignores_unrelated_params() -> None:
    request = _request_with_params(
        text="abc",
        flags=0,
        supplemental_case=FakeParityCase(unsupported_backends=("stdlib",)),
    )

    assert _unsupported_backend_skip_reason(request, "rebar") is None


def test_unsupported_backend_skip_reason_defaults_missing_reason() -> None:
    request = _request_with_params(
        supplemental_case=FakeParityCase(unsupported_backends=("rebar",))
    )

    assert (
        _unsupported_backend_skip_reason(request, "rebar")
        == "rebar backend unsupported for this parity case"
    )


def test_unsupported_backend_skip_reason_rejects_multiple_param_sources() -> None:
    request = _request_with_params(
        case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="primary reason",
        ),
        supplemental_case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="secondary reason",
        ),
    )

    with pytest.raises(
        AssertionError,
        match="multiple parametrized values declare unsupported_backends",
    ):
        _unsupported_backend_skip_reason(request, "rebar")
