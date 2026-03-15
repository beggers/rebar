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
    case = getattr(getattr(request.node, "callspec", None), "params", {}).get("case")
    unsupported_backends = getattr(case, "unsupported_backends", ())
    if request.param in unsupported_backends:
        reason = getattr(
            case,
            "unsupported_backend_reason",
            f"{request.param} backend unsupported for this parity case",
        )
        pytest.skip(reason)

    if request.param == "stdlib":
        return ("stdlib", re)
    return ("rebar", rebar)
