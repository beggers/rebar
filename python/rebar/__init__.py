"""Scaffold-only package surface for the future `re`-compatible API.

The public drop-in module API will live in this package. The native extension
boundary is `rebar._rebar`, built through PyO3 and maturin.
"""

from __future__ import annotations

from typing import Final

TARGET_CPYTHON_SERIES: Final[str] = "3.12.x"
SCAFFOLD_STATUS: Final[str] = "scaffold-only"
NATIVE_MODULE_NAME: Final[str] = "rebar._rebar"

try:
    from . import _rebar as _native
except ImportError:
    _native = None

__all__ = [
    "NATIVE_MODULE_NAME",
    "SCAFFOLD_STATUS",
    "TARGET_CPYTHON_SERIES",
    "compile",
    "native_module_loaded",
]


def native_module_loaded() -> bool:
    """Report whether the optional scaffold extension is available."""

    return _native is not None


def compile(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.compile` surface."""

    if _native is not None:
        return _native.scaffold_compile(*_args, **_kwargs)
    raise NotImplementedError(
        "rebar.compile() is a scaffold placeholder; the native `re`-compatible API "
        "has not been implemented yet"
    )
