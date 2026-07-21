#!/usr/bin/env python3
"""Run the vendored CPython 3.14.6 public re tests as a compatibility oracle."""

import argparse
import contextlib
import gc
import hashlib
import importlib
import importlib.util
import io
import json
import platform
import subprocess
import sys
import time
import types
import unittest
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "oracle" / "cpython-3.14.6"
TEST_RE = UPSTREAM / "test_re.py"
RE_TESTS = UPSTREAM / "re_tests.py"
LICENSE = UPSTREAM / "LICENSE"
MANIFEST = UPSTREAM / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
TARBALL_HASH = "143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63"
SOURCE_HASHES = {"test_re.py": "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2", "re_tests.py": "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab", "LICENSE": "b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231"}
PUBLIC_CLASSES = ("ReTests", "PatternReprTests", "ExternalTests")
WAIVERS = {
    "ReTests.test_re_groupref_overflow": "PRIVATE-CONSTANTS: imports re._constants.MAXGROUPS",
    "ReTests.test_large_search": "RESOURCE-BIGMEM: requires a multi-gigabyte test resource",
    "ReTests.test_large_subn": "RESOURCE-BIGMEM: requires a multi-gigabyte test resource",
    "ReTests.test_search_anchor_at_beginning": "PERFORMANCE-ASSERTION: timing threshold belongs in the frozen performance oracle",
    "ReTests.test_regression_gh94675": "ENV-MULTIPROCESSING: sandbox cannot create the required forkserver socket",
    "ReTests.test_memory_leaks": "PRIVATE-DEBUG-HOOK: requires Pattern._fail_after from a debug CPython build",
}
CLASS_WAIVERS = {"DebugTests": "PRIVATE-DEBUG-TEXT: stdlib opcode/debug text is not a public contract", "ImplementationTest": "PRIVATE-INTERNAL-COMPILER: checks re._compiler, _sre, and deprecated internal modules"}
TIMEOUT_SECONDS = 8


def runtime():
    if platform.python_implementation() != "CPython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError(f"CPython re oracle requires CPython 3.14.6, got {platform.python_implementation()} {sys.version.split()[0]}")


def source_check():
    actual = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (TEST_RE, RE_TESTS, LICENSE)}
    if actual != SOURCE_HASHES:
        raise RuntimeError(f"vendored CPython source drift: {actual}")
    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md hash changed")


def support_shim():
    package = types.ModuleType("test")
    package.__path__ = [str(UPSTREAM)]
    support = types.ModuleType("test.support")
    warning_helper = types.ModuleType("test.support.warnings_helper")

    def ignored(*, category=Warning):
        def decorate(function):
            def wrapped(*args, **kwargs):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category)
                    return function(*args, **kwargs)

            return wrapped

        return decorate

    class Stopwatch:
        def __enter__(self):
            self.started = time.monotonic()
            return self

        def __exit__(self, exc_type, exc, tb):
            self.elapsed = time.monotonic() - self.started

    @contextlib.contextmanager
    def captured_stdout():
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            yield output

    def bigmemtest(*, size, memuse):
        return unittest.skip(f"RESOURCE-BIGMEM: size={size}, memuse={memuse}")

    def requires_resource(resource):
        return unittest.skip(f"RESOURCE-{resource.upper()}: disabled in compatibility oracle")

    def disallow(testcase, value):
        with testcase.assertRaises(TypeError):
            value()

    warning_helper.ignore_warnings = ignored
    support.gc_collect = gc.collect
    support.bigmemtest = bigmemtest
    support._2G = 2 * 1024 ** 3
    support.cpython_only = lambda value: value
    support.captured_stdout = captured_stdout
    support.check_disallow_instantiation = disallow
    support.linked_to_musl = lambda: False
    support.warnings_helper = warning_helper
    support.SHORT_TIMEOUT = TIMEOUT_SECONDS
    support.Stopwatch = Stopwatch
    support.requires_resource = requires_resource
    package.support = support
    sys.modules["test"] = package
    sys.modules["test.support"] = support
    sys.modules["test.support.warnings_helper"] = warning_helper
    corpus_spec = importlib.util.spec_from_file_location("test.re_tests", RE_TESTS)
    corpus = importlib.util.module_from_spec(corpus_spec)
    corpus_spec.loader.exec_module(corpus)
    sys.modules["test.re_tests"] = corpus
    package.re_tests = corpus
    return corpus


def load_tests(module_name):
    source_check()
    corpus = support_shim()
    source = TEST_RE.read_text(encoding="utf-8")
    if module_name != "re":
        source = source.replace("\nimport re\n", f"\nimport {module_name} as re\n", 1)
        source = source.replace("from re import Scanner", "Scanner = getattr(re, 'Scanner', None)", 1)
    namespace = {"__name__": "rebar_cpython_re_oracle", "__file__": str(TEST_RE)}
    exec(compile(source, str(TEST_RE), "exec"), namespace)
    return namespace, corpus


def test_ids(namespace):
    result = []
    for class_name in PUBLIC_CLASSES:
        cls = namespace[class_name]
        result.extend(f"{class_name}.{name}" for name in unittest.defaultTestLoader.getTestCaseNames(cls))
    return sorted(result)


def run_one(module_name, test_id):
    namespace, _corpus = load_tests(module_name)
    class_name, method = test_id.split(".", 1)
    if test_id in WAIVERS:
        return {"test": test_id, "status": "waived", "reason": WAIVERS[test_id]}
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(unittest.TestSuite([namespace[class_name](method)]))
    failures = [{"test": str(test), "trace": trace} for test, trace in [*result.failures, *result.errors]]
    if failures:
        return {"test": test_id, "status": "failed", "failures": failures, "skipped": len(result.skipped)}
    return {"test": test_id, "status": "skipped" if result.skipped else "passed", "skipped": len(result.skipped), "reason": result.skipped[0][1] if result.skipped else None}


def one(args):
    runtime()
    print(json.dumps(run_one(args.module, args.test), ensure_ascii=False, sort_keys=True))


def freeze(_args):
    runtime()
    source_check()
    namespace, corpus = load_tests("re")
    ids = test_ids(namespace)
    selected = [value for value in ids if value not in WAIVERS]
    outcomes = {"succeed": sum(item[2] == corpus.SUCCEED for item in corpus.tests), "fail": sum(item[2] == corpus.FAIL for item in corpus.tests), "syntax_error": sum(item[2] == corpus.SYNTAX_ERROR for item in corpus.tests)}
    manifest = {"schema": "rebar-cpython-re-oracle-v1", "python": "3.14.6", "implementation": "CPython", "source_url": "https://www.python.org/ftp/python/3.14.6/Python-3.14.6.tar.xz", "source_tarball_sha256": TARBALL_HASH, "goal_sha256": GOAL_HASH, "source_sha256": SOURCE_HASHES, "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "public_classes": list(PUBLIC_CLASSES), "test_methods": len(ids), "selected_methods": len(selected), "corpus_cases": len(corpus.tests), "corpus_outcomes": outcomes, "benchmark_patterns": len(corpus.benchmarks), "timeout_seconds": TIMEOUT_SECONDS, "named_waivers": {**CLASS_WAIVERS, **WAIVERS}}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def verify(args):
    runtime()
    source_check()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    actual_runner = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if actual_runner != manifest["runner_sha256"]:
        raise RuntimeError("frozen CPython oracle runner drift")
    namespace, corpus = load_tests("re")
    ids = test_ids(namespace)
    if len(ids) != manifest["test_methods"] or len(corpus.tests) != manifest["corpus_cases"]:
        raise RuntimeError("frozen CPython test count drift")
    selected = [value for value in ids if value not in WAIVERS]
    if args.test:
        if args.test not in ids:
            raise RuntimeError(f"unknown test ID: {args.test}")
        selected = [args.test]
    records = []
    for test_id in selected:
        try:
            completed = subprocess.run([sys.executable, str(Path(__file__)), "one", "--module", args.module, "--test", test_id], cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT_SECONDS + 2, check=False)
        except subprocess.TimeoutExpired:
            records.append({"test": test_id, "status": "timeout", "seconds": TIMEOUT_SECONDS + 2})
            continue
        if completed.returncode or not completed.stdout.strip():
            records.append({"test": test_id, "status": "crash", "returncode": completed.returncode, "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:]})
            continue
        try:
            records.append(json.loads(completed.stdout.splitlines()[-1]))
        except json.JSONDecodeError:
            records.append({"test": test_id, "status": "invalid-output", "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:]})
    failed = [record for record in records if record["status"] not in {"passed", "skipped", "waived"}]
    output = {"schema": "rebar-cpython-re-result-v1", "module": args.module, "methods": len(records), "passed": sum(record["status"] == "passed" for record in records), "skipped": sum(record["status"] == "skipped" for record in records), "failed": len(failed), "timeouts": sum(record["status"] == "timeout" for record in records), "crashes": sum(record["status"] in {"crash", "invalid-output"} for record in records), "source_sha256": SOURCE_HASHES, "runner_sha256": actual_runner, "records": records}
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "records"}, sort_keys=True))
    for record in failed[:80]:
        reason = record["status"]
        if record.get("failures"):
            reason = record["failures"][0]["trace"].splitlines()[-1]
        print(f"{record['test']}: {reason}", file=sys.stderr)
    if failed:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("freeze").set_defaults(function=freeze)
    one_parser = commands.add_parser("one")
    one_parser.add_argument("--module", required=True)
    one_parser.add_argument("--test", required=True)
    one_parser.set_defaults(function=one)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--module", default="re")
    verify_parser.add_argument("--test")
    verify_parser.add_argument("--output")
    verify_parser.set_defaults(function=verify)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
