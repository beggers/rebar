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

from rebar_harness.benchmarks import load_manifests


def _write_manifest(
    directory: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = directory / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("manifest_sources", "error_pattern"),
    [
        pytest.param(
            (
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-a",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-b",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark manifest id .*duplicate-benchmark-manifest-id",
            id="duplicate-manifest-id",
        ),
        pytest.param(
            (
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-a",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-b",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark workload id .*duplicate-benchmark-workload-id",
            id="duplicate-workload-id",
        ),
    ],
)
def test_load_manifests_rejects_duplicate_ids(
    manifest_sources: tuple[str, str],
    error_pattern: str,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = pathlib.Path(temp_dir)
        manifest_paths = [
            _write_manifest(temp_root, f"manifest_{index}.py", source)
            for index, source in enumerate(manifest_sources, start=1)
        ]

        with pytest.raises(ValueError, match=error_pattern):
            load_manifests(manifest_paths)
