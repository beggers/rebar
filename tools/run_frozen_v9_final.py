#!/usr/bin/env python3
"""Run the unchanged, hash-frozen final protocol with its missing time global."""

import hashlib
import importlib.util
import json
import runpy
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROTOCOL_PATH = ROOT / "tools" / "rust_v9_holdout_protocol.py"
PROTOCOL_MODULE = "tools.rust_v9_holdout_protocol"
PROTOCOL_SHA256 = "a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219"


class FrozenBootstrapError(RuntimeError):
    """The exact original frozen protocol or supported invocation was rejected."""


def verify_protocol(expected_sha256=PROTOCOL_SHA256, module=PROTOCOL_MODULE):
    if module != PROTOCOL_MODULE:
        raise FrozenBootstrapError("the frozen protocol module was changed")
    try:
        protocol_path = PROTOCOL_PATH.resolve(strict=True)
        actual_sha256 = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    except (OSError, RuntimeError, ValueError) as error:
        raise FrozenBootstrapError("cannot read the frozen protocol") from error
    if actual_sha256 != expected_sha256:
        raise FrozenBootstrapError("the frozen protocol SHA-256 was changed")

    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        spec = importlib.util.find_spec(module)
        if spec is None or spec.origin is None:
            raise FrozenBootstrapError("the frozen protocol has no import source")
        module_path = Path(spec.origin).resolve(strict=True)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        raise FrozenBootstrapError("cannot resolve the frozen protocol module") from error
    if module_path != protocol_path:
        raise FrozenBootstrapError("the frozen protocol resolved to a different source")
    return actual_sha256


def classify_arguments(arguments):
    if arguments == ["--self-test"]:
        return "--self-test"
    if arguments and arguments[0] == "final":
        return "final"
    raise FrozenBootstrapError("only 'final' or an exact '--self-test' is supported")


def self_test(actual_sha256):
    rejections = []
    checks = (
        (
            "mismatched-protocol-hash",
            lambda: verify_protocol("0" * 64, PROTOCOL_MODULE),
        ),
        (
            "mismatched-protocol-module",
            lambda: verify_protocol(PROTOCOL_SHA256, "tools.invalid_frozen_protocol"),
        ),
        ("unsupported-command", lambda: classify_arguments(["verify"])),
        (
            "unsupported-self-test-arguments",
            lambda: classify_arguments(["--self-test", "final"]),
        ),
    )
    for label, check in checks:
        try:
            check()
        except FrozenBootstrapError:
            rejections.append(label)
        else:
            raise FrozenBootstrapError("synthetic rejection did not fail closed")

    print(
        json.dumps(
            {
                "schema": "rebar-v9-frozen-final-bootstrap-self-test-v1",
                "protocol_sha256": actual_sha256,
                "checks": 1 + len(rejections),
                "rejections": rejections,
                "candidate_imported": False,
                "protocol_executed": False,
                "opening_read": False,
                "hidden_cases_generated": 0,
                "timing_performed": False,
                "passed": True,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


def main():
    command = classify_arguments(sys.argv[1:])
    actual_sha256 = verify_protocol()
    if command == "--self-test":
        return self_test(actual_sha256)
    runpy.run_module(
        PROTOCOL_MODULE,
        run_name="__main__",
        init_globals={"time": time},
        alter_sys=True,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FrozenBootstrapError as error:
        print(f"frozen final bootstrap rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error
