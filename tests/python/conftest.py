from __future__ import annotations

import re

import pytest


import rebar


def _unsupported_backend_skip_reason(
    request: pytest.FixtureRequest,
    backend_name: str,
) -> str | None:
    callspec = getattr(request.node, "callspec", None)
    if callspec is None:
        return None

    matching_param_names: list[str] = []
    skip_reason: str | None = None
    for param_name, value in callspec.params.items():
        unsupported_backends = getattr(value, "unsupported_backends", ())
        if backend_name not in unsupported_backends:
            continue

        matching_param_names.append(param_name)
        reason = getattr(value, "unsupported_backend_reason", None)
        if not reason:
            reason = f"{backend_name} backend unsupported for this parity case"
        if skip_reason is None:
            skip_reason = reason

    if len(matching_param_names) > 1:
        raise AssertionError(
            "multiple parametrized values declare unsupported_backends for "
            f"{backend_name!r}: {tuple(matching_param_names)}"
        )

    return skip_reason


@pytest.fixture(autouse=True)
def purge_regex_caches() -> None:
    re.purge()
    rebar.purge()
    yield
    re.purge()
    rebar.purge()


@pytest.fixture(
    params=[
        pytest.param("stdlib", id="stdlib"),
        pytest.param(
            "rebar",
            id="rebar",
            marks=pytest.mark.skipif(
                not rebar.native_module_loaded(),
                reason="backend parity requires rebar._rebar",
            ),
        ),
    ]
)
def regex_backend(request: pytest.FixtureRequest) -> tuple[str, object]:
    skip_reason = _unsupported_backend_skip_reason(request, request.param)
    if skip_reason is not None:
        pytest.skip(skip_reason)

    if request.param == "stdlib":
        return ("stdlib", re)
    return ("rebar", rebar)
