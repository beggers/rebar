from __future__ import annotations

import pathlib
import re
import sys
import tempfile
import textwrap
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness.benchmarks import load_manifest, workload_to_payload


class PythonBenchmarkManifestContractTest(unittest.TestCase):
    maxDiff = None

    def _write_manifest(
        self,
        directory: pathlib.Path,
        filename: str,
        source: str,
    ) -> pathlib.Path:
        path = directory / filename
        path.write_text(textwrap.dedent(source), encoding="utf-8")
        return path

    def test_python_benchmark_manifest_materializes_callable_replacement_descriptors(
        self,
    ) -> None:
        manifest_source = """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "python-benchmark-loader-contract",
            "defaults": {
                "warmup_iterations": 2,
                "sample_iterations": 3,
                "timed_samples": 4,
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
            },
            "workloads": [
                {
                    "id": "module-sub-callable-numbered-contract-str",
                    "bucket": "module-sub",
                    "family": "module",
                    "operation": "module.sub",
                    "pattern": r"a((bc)+)d",
                    "replacement": {
                        "type": "callable_match_group",
                        "group": 1,
                        "suffix": "x",
                    },
                    "haystack": "zzabcbcdzz",
                    "count": 0,
                    "categories": ["replacement", "callable", "numbered-group", "str"],
                    "notes": [
                        "Ensures Python-backed benchmark manifests materialize numbered callable replacement descriptors."
                    ],
                },
                {
                    "id": "pattern-subn-callable-named-contract-str",
                    "bucket": "pattern-subn",
                    "family": "module",
                    "operation": "pattern.subn",
                    "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                    "replacement": {
                        "type": "callable_match_group",
                        "group": "inner",
                        "prefix": "<",
                        "suffix": ">",
                    },
                    "haystack": "zzabcbcdabcbcdzz",
                    "count": 1,
                    "cache_mode": "purged",
                    "timing_scope": "pattern-helper-call",
                    "categories": ["replacement", "callable", "named-group", "str"],
                    "notes": [
                        "Ensures Python-backed benchmark manifests materialize named callable replacement descriptors."
                    ],
                },
                {
                    "id": "module-sub-callable-constant-contract-bytes",
                    "bucket": "module-sub",
                    "family": "module",
                    "operation": "module.sub",
                    "pattern": r"a((bc)+)d",
                    "replacement": {
                        "type": "callable_constant",
                        "value": {
                            "type": "bytes",
                            "value": "CONST",
                            "encoding": "ascii",
                        },
                    },
                    "haystack": "zzabcbcdzz",
                    "text_model": "bytes",
                    "categories": ["replacement", "callable", "constant", "bytes"],
                    "notes": [
                        "Ensures Python-backed benchmark manifests keep bytes-aware callable constants available for subprocess serialization and runtime materialization."
                    ],
                },
            ],
        }
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = self._write_manifest(
                pathlib.Path(temp_dir),
                "python_benchmark_loader_contract.py",
                manifest_source,
            )
            manifest, workloads = load_manifest(manifest_path)

        self.assertEqual(manifest["manifest_id"], "python-benchmark-loader-contract")
        self.assertEqual(manifest["defaults"]["warmup_iterations"], 2)
        self.assertEqual([workload.workload_id for workload in workloads], [
            "module-sub-callable-numbered-contract-str",
            "pattern-subn-callable-named-contract-str",
            "module-sub-callable-constant-contract-bytes",
        ])

        numbered_workload = workloads[0]
        self.assertEqual(numbered_workload.warmup_iterations, 2)
        self.assertEqual(numbered_workload.sample_iterations, 3)
        self.assertEqual(numbered_workload.timed_samples, 4)
        self.assertEqual(numbered_workload.pattern_payload(), r"a((bc)+)d")
        self.assertEqual(numbered_workload.haystack_payload(), "zzabcbcdzz")
        numbered_replacement = numbered_workload.replacement_payload()
        self.assertTrue(callable(numbered_replacement))
        self.assertEqual(numbered_replacement.__qualname__, "callable_match_group")
        numbered_match = re.search(
            numbered_workload.pattern_payload(),
            numbered_workload.haystack_payload(),
        )
        self.assertIsNotNone(numbered_match)
        self.assertEqual(numbered_replacement(numbered_match), "bcbcx")
        self.assertEqual(
            workload_to_payload(numbered_workload)["replacement"],
            {
                "type": "callable_match_group",
                "group": 1,
                "suffix": "x",
            },
        )

        named_workload = workloads[1]
        self.assertEqual(named_workload.cache_mode, "purged")
        self.assertEqual(named_workload.timing_scope, "pattern-helper-call")
        named_replacement = named_workload.replacement_payload()
        self.assertTrue(callable(named_replacement))
        self.assertEqual(named_replacement.__qualname__, "callable_match_group")
        named_match = re.search(
            named_workload.pattern_payload(),
            named_workload.haystack_payload(),
        )
        self.assertIsNotNone(named_match)
        self.assertEqual(named_replacement(named_match), "<bc>")
        self.assertEqual(
            workload_to_payload(named_workload)["replacement"],
            {
                "type": "callable_match_group",
                "group": "inner",
                "prefix": "<",
                "suffix": ">",
            },
        )

        constant_bytes_workload = workloads[2]
        self.assertEqual(constant_bytes_workload.text_model, "bytes")
        self.assertEqual(constant_bytes_workload.pattern_payload(), rb"a((bc)+)d")
        self.assertEqual(constant_bytes_workload.haystack_payload(), b"zzabcbcdzz")
        constant_bytes_replacement = constant_bytes_workload.replacement_payload()
        self.assertTrue(callable(constant_bytes_replacement))
        self.assertEqual(constant_bytes_replacement.__qualname__, "callable_constant")
        constant_bytes_match = re.search(
            constant_bytes_workload.pattern_payload(),
            constant_bytes_workload.haystack_payload(),
        )
        self.assertIsNotNone(constant_bytes_match)
        self.assertEqual(constant_bytes_replacement(constant_bytes_match), b"CONST")
        self.assertEqual(
            workload_to_payload(constant_bytes_workload)["replacement"],
            {
                "type": "callable_constant",
                "value": {
                    "type": "bytes",
                    "value": "CONST",
                    "encoding": "ascii",
                },
            },
        )

    def test_python_benchmark_manifest_rejects_missing_and_non_dict_manifest_values(
        self,
    ) -> None:
        invalid_modules = (
            (
                "missing_manifest.py",
                "WORKLOADS = []",
                r"is missing a MANIFEST value",
            ),
            (
                "non_dict_manifest.py",
                "MANIFEST = ['not-a-dict']",
                r"must be a dict",
            ),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            for filename, source, error_pattern in invalid_modules:
                with self.subTest(filename=filename):
                    manifest_path = self._write_manifest(temp_root, filename, source)
                    with self.assertRaisesRegex(ValueError, error_pattern):
                        load_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
