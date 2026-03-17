from __future__ import annotations

from dataclasses import dataclass
import re
from types import SimpleNamespace

import pytest

import rebar
from tests.python import conftest as python_conftest
from tests.python.conftest import _unsupported_backend_skip_reason


@dataclass(frozen=True)
class FakeParityCase:
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


def _request_with_params(**params: object) -> object:
    return SimpleNamespace(node=SimpleNamespace(callspec=SimpleNamespace(params=params)))


def _fixture_request(backend_name: str, **params: object) -> object:
    return SimpleNamespace(
        param=backend_name,
        node=SimpleNamespace(callspec=SimpleNamespace(params=params)),
    )


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


def test_purge_regex_caches_calls_both_backends_before_and_after_test(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def _record_stdlib_purge() -> None:
        calls.append("stdlib")

    def _record_rebar_purge() -> None:
        calls.append("rebar")

    monkeypatch.setattr(python_conftest.re, "purge", _record_stdlib_purge)
    monkeypatch.setattr(python_conftest.rebar, "purge", _record_rebar_purge)

    fixture_gen = python_conftest.purge_regex_caches.__wrapped__()

    next(fixture_gen)
    assert calls == ["stdlib", "rebar"]

    with pytest.raises(StopIteration):
        next(fixture_gen)

    assert calls == ["stdlib", "rebar", "stdlib", "rebar"]


def test_regex_backend_fixture_returns_stdlib_backend_module() -> None:
    request = _fixture_request("stdlib")

    assert python_conftest.regex_backend.__wrapped__(request) == ("stdlib", re)


@pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="rebar backend fixture only resolves when rebar._rebar is available",
)
def test_regex_backend_fixture_returns_rebar_backend_module() -> None:
    request = _fixture_request("rebar")

    assert python_conftest.regex_backend.__wrapped__(request) == ("rebar", rebar)


def test_regex_backend_fixture_propagates_unsupported_backend_skips() -> None:
    request = _fixture_request(
        "rebar",
        case=FakeParityCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="feature slice is stdlib-only",
        ),
    )

    with pytest.raises(pytest.skip.Exception, match="feature slice is stdlib-only"):
        python_conftest.regex_backend.__wrapped__(request)
