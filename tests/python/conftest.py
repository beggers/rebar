from __future__ import annotations

import re

import pytest


import rebar

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
    callspec = getattr(request.node, "callspec", None)
    if callspec is not None:
        matching_param_names: list[str] = []
        skip_reason: str | None = None
        for param_name, value in callspec.params.items():
            unsupported_backends = getattr(value, "unsupported_backends", ())
            if request.param not in unsupported_backends:
                continue

            matching_param_names.append(param_name)
            reason = getattr(value, "unsupported_backend_reason", None)
            if not reason:
                reason = f"{request.param} backend unsupported for this parity case"
            if skip_reason is None:
                skip_reason = reason

        if len(matching_param_names) > 1:
            raise AssertionError(
                "multiple parametrized values declare unsupported_backends for "
                f"{request.param!r}: {tuple(matching_param_names)}"
            )
        if skip_reason is not None:
            pytest.skip(skip_reason)

    if request.param == "stdlib":
        return ("stdlib", re)
    return ("rebar", rebar)
