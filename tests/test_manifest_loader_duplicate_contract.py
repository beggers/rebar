from __future__ import annotations

import pathlib
import sys
import tempfile
import textwrap
from collections.abc import Callable, Sequence

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness.benchmarks import load_manifests
from rebar_harness.correctness import load_fixture_manifests


def _write_python_module(
    directory: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = directory / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("loader", "module_sources", "error_pattern"),
    [
        pytest.param(
            load_manifests,
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
            id="benchmark-manifest-id",
        ),
        pytest.param(
            load_manifests,
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
            id="benchmark-workload-id",
        ),
        pytest.param(
            load_fixture_manifests,
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
            id="correctness-manifest-id",
        ),
        pytest.param(
            load_fixture_manifests,
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
            id="correctness-case-id",
        ),
    ],
)
def test_python_manifest_loaders_reject_duplicate_ids(
    loader: Callable[[Sequence[pathlib.Path]], object],
    module_sources: tuple[str, str],
    error_pattern: str,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = pathlib.Path(temp_dir)
        manifest_paths = [
            _write_python_module(temp_root, f"manifest_{index}.py", source)
            for index, source in enumerate(module_sources, start=1)
        ]

        with pytest.raises(ValueError, match=error_pattern):
            loader(manifest_paths)
