"""Scaffold-only package surface for the future `re`-compatible API.

The public drop-in module API will live in this package. The native extension
boundary is `rebar._rebar`, built through PyO3 and maturin.
"""

from __future__ import annotations

import enum
import importlib.util
import re as _stdlib_re
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

def _placeholder_message(helper_name: str) -> str:
    return (
        f"rebar.{helper_name}() is a scaffold placeholder; "
        "the `re`-compatible API is not implemented yet"
    )


def _raise_placeholder(helper_name: str) -> object:
    if _native is not None:
        return _native.scaffold_raise(helper_name)
    raise NotImplementedError(_placeholder_message(helper_name))


class RegexFlag(enum.IntFlag):
    """CPython-shaped exported flag enum for the scaffold package."""

    NOFLAG = 0
    TEMPLATE = 1
    IGNORECASE = 2
    LOCALE = 4
    MULTILINE = 8
    DOTALL = 16
    UNICODE = 32
    VERBOSE = 64
    DEBUG = 128
    ASCII = 256


NOFLAG = RegexFlag.NOFLAG
TEMPLATE = RegexFlag.TEMPLATE
T = TEMPLATE
IGNORECASE = RegexFlag.IGNORECASE
I = IGNORECASE
LOCALE = RegexFlag.LOCALE
L = LOCALE
MULTILINE = RegexFlag.MULTILINE
M = MULTILINE
DOTALL = RegexFlag.DOTALL
S = DOTALL
UNICODE = RegexFlag.UNICODE
U = UNICODE
VERBOSE = RegexFlag.VERBOSE
X = VERBOSE
DEBUG = RegexFlag.DEBUG
ASCII = RegexFlag.ASCII
A = ASCII
error = _stdlib_re.error


class _NonInstantiableScaffoldType(type):
    def __call__(cls, *_args: object, **_kwargs: object) -> object:
        raise TypeError(f"cannot create '{cls.__module__}.{cls.__name__}' instances")


class Pattern(metaclass=_NonInstantiableScaffoldType):
    """Placeholder export for the future compiled-pattern type."""


class Match(metaclass=_NonInstantiableScaffoldType):
    """Placeholder export for the future match-result type."""


__all__ = [
    "match",
    "fullmatch",
    "search",
    "sub",
    "subn",
    "split",
    "findall",
    "finditer",
    "compile",
    "purge",
    "template",
    "escape",
    "error",
    "Pattern",
    "Match",
    "A",
    "I",
    "L",
    "M",
    "S",
    "X",
    "U",
    "ASCII",
    "IGNORECASE",
    "LOCALE",
    "MULTILINE",
    "DOTALL",
    "VERBOSE",
    "UNICODE",
    "NOFLAG",
    "RegexFlag",
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

    return _raise_placeholder("compile")


def search(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.search` surface."""

    return _raise_placeholder("search")


def match(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.match` surface."""

    return _raise_placeholder("match")


def fullmatch(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.fullmatch` surface."""

    return _raise_placeholder("fullmatch")


def split(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.split` surface."""

    return _raise_placeholder("split")


def findall(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.findall` surface."""

    return _raise_placeholder("findall")


def finditer(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.finditer` surface."""

    return _raise_placeholder("finditer")


def sub(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.sub` surface."""

    return _raise_placeholder("sub")


def subn(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.subn` surface."""

    return _raise_placeholder("subn")


def template(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.template` surface."""

    return _raise_placeholder("template")


def escape(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.escape` surface."""

    return _raise_placeholder("escape")


def purge() -> None:
    """Placeholder for the future cache-management hook."""

    if _native is not None:
        _native.scaffold_purge()
    return None
