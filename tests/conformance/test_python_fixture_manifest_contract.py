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

from rebar_harness.correctness import load_fixture_manifest, load_fixture_manifests


class PythonFixtureManifestContractTest(unittest.TestCase):
    maxDiff = None

    def _write_fixture(
        self,
        directory: pathlib.Path,
        filename: str,
        source: str,
    ) -> pathlib.Path:
        path = directory / filename
        path.write_text(textwrap.dedent(source), encoding="utf-8")
        return path

    def test_python_fixture_manifest_materializes_callable_replacement_descriptors(
        self,
    ) -> None:
        fixture_source = """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "quantified-nested-group-callable-loader-contract",
            "layer": "module_workflow",
            "suite_id": "collection.replacement.quantified_nested_group.callable.contract",
            "defaults": {
                "text_model": "str",
            },
            "cases": [
                {
                    "id": "module-sub-callable-numbered-contract-str",
                    "operation": "module_call",
                    "family": "quantified_nested_group_numbered_callable_contract",
                    "helper": "sub",
                    "args": [
                        r"a((bc)+)d",
                        {
                            "type": "callable_match_group",
                            "group": 1,
                            "suffix": "x",
                        },
                        "zzabcbcdzz",
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "str"],
                    "notes": [
                        "Ensures Python-backed fixtures can materialize numbered callable replacement descriptors for quantified nested-group workflows."
                    ],
                },
                {
                    "id": "pattern-subn-callable-named-contract-str",
                    "operation": "pattern_call",
                    "family": "quantified_nested_group_named_callable_contract",
                    "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                    "helper": "subn",
                    "args": [
                        {
                            "type": "callable_match_group",
                            "group": "inner",
                            "prefix": "<",
                            "suffix": ">",
                        },
                        "zzabcbcdabcbcdzz",
                        1,
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "str"],
                    "notes": [
                        "Ensures Python-backed fixtures can materialize named callable replacement descriptors for quantified nested-group workflows."
                    ],
                },
                {
                    "id": "module-sub-callable-constant-contract-str",
                    "operation": "module_call",
                    "family": "quantified_nested_group_constant_callable_contract",
                    "helper": "sub",
                    "args": [
                        r"a((bc)+)d",
                        {
                            "type": "callable_constant",
                            "value": "CONST",
                        },
                        "zzabcdzz",
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "str"],
                    "notes": [
                        "Ensures Python-backed fixtures can materialize constant callable descriptors without falling back to raw dict payloads."
                    ],
                },
            ],
        }
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = self._write_fixture(
                pathlib.Path(temp_dir),
                "quantified_nested_group_callable_fixture.py",
                fixture_source,
            )
            manifest, cases = load_fixture_manifest(fixture_path)

        self.assertEqual(
            manifest.manifest_id,
            "quantified-nested-group-callable-loader-contract",
        )
        self.assertEqual(manifest.layer, "module_workflow")
        self.assertEqual(
            manifest.suite_id,
            "collection.replacement.quantified_nested_group.callable.contract",
        )
        self.assertEqual([case.case_id for case in cases], [
            "module-sub-callable-numbered-contract-str",
            "pattern-subn-callable-named-contract-str",
            "module-sub-callable-constant-contract-str",
        ])

        numbered_case = cases[0]
        self.assertEqual(numbered_case.helper, "sub")
        self.assertEqual(numbered_case.args[0], r"a((bc)+)d")
        self.assertTrue(callable(numbered_case.args[1]))
        numbered_match = re.search(r"a((bc)+)d", "zzabcbcdzz")
        self.assertIsNotNone(numbered_match)
        self.assertEqual(numbered_case.args[1](numbered_match), "bcbcx")
        self.assertEqual(
            numbered_case.serialized_args()[1],
            {
                "type": "callable",
                "module": "rebar_harness.correctness",
                "qualname": "callable_match_group",
            },
        )

        named_case = cases[1]
        self.assertEqual(named_case.helper, "subn")
        self.assertEqual(
            named_case.pattern_payload(),
            r"a(?P<outer>(?P<inner>bc)+)d",
        )
        self.assertTrue(callable(named_case.args[0]))
        named_match = re.search(named_case.pattern_payload(), "zzabcbcdzz")
        self.assertIsNotNone(named_match)
        self.assertEqual(named_case.args[0](named_match), "<bc>")
        self.assertEqual(
            named_case.serialized_args()[0],
            {
                "type": "callable",
                "module": "rebar_harness.correctness",
                "qualname": "callable_match_group",
            },
        )

        constant_case = cases[2]
        self.assertEqual(constant_case.helper, "sub")
        self.assertTrue(callable(constant_case.args[1]))
        constant_match = re.search(r"a((bc)+)d", "zzabcdzz")
        self.assertIsNotNone(constant_match)
        self.assertEqual(constant_case.args[1](constant_match), "CONST")
        self.assertEqual(
            constant_case.serialized_args()[1],
            {
                "type": "callable",
                "module": "rebar_harness.correctness",
                "qualname": "callable_constant",
            },
        )

    def test_python_fixture_manifest_materializes_bytes_callables_without_aliasing_defaults(
        self,
    ) -> None:
        fixture_source = """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "bytes-callable-loader-contract",
            "layer": "module_workflow",
            "suite_id": "collection.replacement.bytes.callable.contract",
            "defaults": {
                "operation": "pattern_call",
                "helper": "sub",
                "text_model": "bytes",
                "pattern_encoding": "latin-1",
                "args": [
                    {
                        "type": "callable_match_group",
                        "group": 1,
                        "prefix": {
                            "type": "bytes",
                            "value": "<",
                        },
                        "suffix": {
                            "type": "bytes",
                            "value": ">",
                        },
                    },
                    {
                        "type": "bytes",
                        "value": "zzabcbcdzz",
                    },
                ],
                "kwargs": {
                    "count": 1,
                },
            },
            "cases": [
                {
                    "id": "pattern-sub-callable-match-group-default-a-bytes",
                    "family": "bytes_callable_match_group_default",
                    "pattern": r"a((bc)+)d",
                },
                {
                    "id": "pattern-sub-callable-match-group-default-b-bytes",
                    "family": "bytes_callable_match_group_default",
                    "pattern": r"a((bc)+)d",
                },
                {
                    "id": "pattern-sub-callable-constant-override-bytes",
                    "family": "bytes_callable_constant_override",
                    "pattern": r"a((bc)+)d",
                    "args": [
                        {
                            "type": "callable_constant",
                            "value": {
                                "type": "bytes",
                                "value": "CONST",
                            },
                        },
                        {
                            "type": "bytes",
                            "value": "zzabcbcdzz",
                        },
                    ],
                },
            ],
        }
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = self._write_fixture(
                pathlib.Path(temp_dir),
                "bytes_callable_fixture.py",
                fixture_source,
            )
            manifest, cases = load_fixture_manifest(fixture_path)

        self.assertEqual(
            manifest.manifest_id,
            "bytes-callable-loader-contract",
        )
        self.assertEqual(manifest.layer, "module_workflow")
        self.assertEqual(
            manifest.suite_id,
            "collection.replacement.bytes.callable.contract",
        )
        self.assertEqual([case.case_id for case in cases], [
            "pattern-sub-callable-match-group-default-a-bytes",
            "pattern-sub-callable-match-group-default-b-bytes",
            "pattern-sub-callable-constant-override-bytes",
        ])

        first_default_case, second_default_case, constant_case = cases

        self.assertEqual(first_default_case.pattern_payload(), b"a((bc)+)d")
        self.assertEqual(second_default_case.pattern_payload(), b"a((bc)+)d")
        self.assertEqual(constant_case.pattern_payload(), b"a((bc)+)d")

        self.assertIsNot(first_default_case.args, second_default_case.args)
        self.assertIsNot(first_default_case.kwargs, second_default_case.kwargs)
        self.assertTrue(callable(first_default_case.args[0]))
        self.assertTrue(callable(second_default_case.args[0]))
        self.assertIsNot(first_default_case.args[0], second_default_case.args[0])
        self.assertEqual(first_default_case.args[1], b"zzabcbcdzz")
        self.assertEqual(first_default_case.serialized_args(), [
            {
                "type": "callable",
                "module": "rebar_harness.correctness",
                "qualname": "callable_match_group",
            },
            {
                "encoding": "latin-1",
                "value": "zzabcbcdzz",
            },
        ])
        self.assertEqual(first_default_case.serialized_kwargs(), {"count": 1})

        match = re.search(first_default_case.pattern_payload(), first_default_case.args[1])
        self.assertIsNotNone(match)
        self.assertEqual(first_default_case.args[0](match), b"<bcbc>")

        first_default_case.args[1] = b"mutated"
        first_default_case.kwargs["count"] = 0
        self.assertEqual(second_default_case.args[1], b"zzabcbcdzz")
        self.assertEqual(second_default_case.kwargs["count"], 1)
        self.assertEqual(constant_case.kwargs["count"], 1)

        self.assertTrue(callable(constant_case.args[0]))
        constant_match = re.search(constant_case.pattern_payload(), constant_case.args[1])
        self.assertIsNotNone(constant_match)
        self.assertEqual(constant_case.args[0](constant_match), b"CONST")
        self.assertEqual(
            constant_case.serialized_args()[0],
            {
                "type": "callable",
                "module": "rebar_harness.correctness",
                "qualname": "callable_constant",
            },
        )
        self.assertEqual(
            constant_case.serialized_args()[1],
            {
                "encoding": "latin-1",
                "value": "zzabcbcdzz",
            },
        )

    def test_python_fixture_manifest_rejects_missing_and_non_dict_manifest_values(
        self,
    ) -> None:
        invalid_modules = (
            (
                "missing_manifest.py",
                "FIXTURE = {}",
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
                    fixture_path = self._write_fixture(temp_root, filename, source)
                    with self.assertRaisesRegex(ValueError, error_pattern):
                        load_fixture_manifest(fixture_path)

    def test_python_fixture_manifest_loader_rejects_duplicate_ids(self) -> None:
        duplicate_modules = (
            (
                (
                    "duplicate_fixture_manifest_a.py",
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
                ),
                (
                    "duplicate_fixture_manifest_b.py",
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
                r"duplicate fixture manifest id .*duplicate-correctness-manifest-id",
            ),
            (
                (
                    "duplicate_fixture_case_a.py",
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
                ),
                (
                    "duplicate_fixture_case_b.py",
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
                r"duplicate fixture case id .*duplicate-correctness-case-id",
            ),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            for first_module, second_module, error_pattern in duplicate_modules:
                with self.subTest(error_pattern=error_pattern):
                    first_path = self._write_fixture(temp_root, *first_module)
                    second_path = self._write_fixture(temp_root, *second_module)
                    with self.assertRaisesRegex(ValueError, error_pattern):
                        load_fixture_manifests([first_path, second_path])


if __name__ == "__main__":
    unittest.main()
