from __future__ import annotations

import pathlib
import sys
import tempfile
import textwrap

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness.correctness import load_fixture_manifests


def _write_fixture(
    directory: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = directory / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("fixture_sources", "error_pattern"),
    [
        pytest.param(
            (
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-correctness-manifest-id",
                    "cases": [
                        {
                            "id": "compile-case-a",
                            "pattern": "abc",
                        },
                    ],
                }
                """,
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-correctness-manifest-id",
                    "cases": [
                        {
                            "id": "compile-case-b",
                            "pattern": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate.*manifest.*duplicate-correctness-manifest-id",
            id="duplicate-manifest-id",
        ),
        pytest.param(
            (
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "correctness-duplicate-case-a",
                    "cases": [
                        {
                            "id": "duplicate-correctness-case-id",
                            "pattern": "abc",
                        },
                    ],
                }
                """,
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "correctness-duplicate-case-b",
                    "cases": [
                        {
                            "id": "duplicate-correctness-case-id",
                            "pattern": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate.*case.*duplicate-correctness-case-id",
            id="duplicate-case-id",
        ),
    ],
)
def test_load_fixture_manifests_rejects_duplicate_ids(
    fixture_sources: tuple[str, str],
    error_pattern: str,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = pathlib.Path(temp_dir)
        fixture_paths = [
            _write_fixture(temp_root, f"fixture_{index}.py", fixture_source)
            for index, fixture_source in enumerate(fixture_sources, start=1)
        ]

        with pytest.raises(ValueError, match=error_pattern):
            load_fixture_manifests(fixture_paths)
