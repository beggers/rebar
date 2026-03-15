from __future__ import annotations

from dataclasses import dataclass
import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


from tests.python.fixture_parity_support import (
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
)


@dataclass(frozen=True)
class OptionalGroupAlternationCase:
    id: str
    pattern: str
    helper: str
    string: str
    use_compiled_pattern: bool = False


COMPILE_PATTERNS = (
    "a(b|c)?d",
    "a(?P<word>b|c)?d",
)

OPTIONAL_GROUP_ALTERNATION_CASES = (
    OptionalGroupAlternationCase(
        id="module-search-numbered-present",
        pattern="a(b|c)?d",
        helper="search",
        string="zzacdzz",
    ),
    OptionalGroupAlternationCase(
        id="pattern-fullmatch-numbered-absent",
        pattern="a(b|c)?d",
        helper="fullmatch",
        string="ad",
        use_compiled_pattern=True,
    ),
    OptionalGroupAlternationCase(
        id="module-search-named-present",
        pattern="a(?P<word>b|c)?d",
        helper="search",
        string="zzabdzz",
    ),
    OptionalGroupAlternationCase(
        id="pattern-fullmatch-named-absent",
        pattern="a(?P<word>b|c)?d",
        helper="fullmatch",
        string="ad",
        use_compiled_pattern=True,
    ),
    OptionalGroupAlternationCase(
        id="module-search-numbered-miss",
        pattern="a(b|c)?d",
        helper="search",
        string="zzaedzz",
    ),
    OptionalGroupAlternationCase(
        id="pattern-fullmatch-named-miss",
        pattern="a(?P<word>b|c)?d",
        helper="fullmatch",
        string="ae",
        use_compiled_pattern=True,
    ),
)


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_compile_matches_cpython_optional_group_alternation_metadata(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, pattern)


@pytest.mark.parametrize(
    "case",
    OPTIONAL_GROUP_ALTERNATION_CASES,
    ids=lambda case: case.id,
)
def test_optional_group_alternation_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: OptionalGroupAlternationCase,
) -> None:
    backend_name, backend = regex_backend

    if case.use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
        )
        observed = getattr(observed_pattern, case.helper)(case.string)
        expected = getattr(expected_pattern, case.helper)(case.string)
    else:
        observed = getattr(backend, case.helper)(case.pattern, case.string)
        expected = getattr(re, case.helper)(case.pattern, case.string)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )

    if expected is None:
        return

    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)
