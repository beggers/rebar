"""Scaffold-only package surface for the future `re`-compatible API.

The public drop-in module API will live in this package. The native extension
boundary is `rebar._rebar`, built through PyO3 and maturin.
"""

from __future__ import annotations

import importlib.util
from typing import Final

TARGET_CPYTHON_SERIES: Final[str] = "3.12.x"
SCAFFOLD_STATUS: Final[str] = "scaffold-only"
NATIVE_MODULE_NAME: Final[str] = "rebar._rebar"

# Only treat a truly missing extension as optional. If a discovered extension
# fails to initialize, surface that error instead of silently masking it.
if importlib.util.find_spec(NATIVE_MODULE_NAME) is None:
    _native = None
else:
    from . import _rebar as _native

__all__ = [
    "NATIVE_MODULE_NAME",
    "SCAFFOLD_STATUS",
    "TARGET_CPYTHON_SERIES",
    "compile",
    "native_module_loaded",
    "native_scaffold_status",
    "native_target_cpython_series",
]


def native_module_loaded() -> bool:
    """Report whether the optional scaffold extension is available."""

    return _native is not None


def native_scaffold_status() -> str | None:
    """Return metadata from the loaded native scaffold when available."""

    if _native is None:
        return None
    return _native.SCAFFOLD_STATUS


def native_target_cpython_series() -> str | None:
    """Return the native module's advertised CPython target when available."""

    if _native is None:
        return None
    return _native.TARGET_CPYTHON_SERIES


def compile(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.compile` surface."""

    if _native is not None:
        return _native.scaffold_compile(*_args, **_kwargs)
    raise NotImplementedError(
        "rebar.compile() is a scaffold placeholder; the native `re`-compatible API "
        "has not been implemented yet"
    )
