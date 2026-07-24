#!/usr/bin/env python3
"""Compare the exact frozen Python regex surface without false recursion.

The four explicitly declared immutable V17/V18 instruction files are the only
inputs to source-only controls. Real Python-reference workers never inspect a
candidate, ownership audit, durable proof, benchmark, or holdout. The candidate
entry is unconditionally blocked before any evidence or candidate access: a
repaired current native graph requires independently frozen V13/V14 evidence
and a separate V20 controller. Frozen old-graph guard helpers remain solely to
preserve truthful failures and exercise candidate-free synthetic controls.
"""

from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import copy
import enum
import hashlib
import importlib
import json
import os
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import traceback
import types
from typing import Any, Callable, Iterator
import weakref


ROOT = Path(os.path.abspath(__file__)).parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

# Import only the two exact, immutable predecessor instruction modules before
# entering the reversible, genuinely file-free source-only effect boundary.
from tools import python_re_public_surface_oracle_stage17 as v17
from tools import python_re_public_surface_oracle_stage18 as v18


SCHEMA = "rebar-python-re-cycle-safe-guarded-public-surface-v19"
SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage19.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V19.md"
CURRENT_GRAPH_CANDIDATE_QUALIFICATION = "BLOCKED"
CURRENT_GRAPH_CANDIDATE_EVIDENCE = "NOT QUALIFIED"
CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON = (
    "the repaired native graph requires independently frozen current V13 "
    "audits, V14 original correctness proofs, and a separate V20 controller"
)

V17_SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage17.py"
V17_SOURCE_SHA256 = (
    "cc36700fd5e43ed409472423a74b7da686804b09c92511d90bec863026c25bf8"
)
V17_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V17.md"
V17_PROTOCOL_SHA256 = (
    "a703805d1cc711488f84bf4d5a4596de8ef194fd47a2116162ec6a490a3da0e5"
)
V18_SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage18.py"
V18_SOURCE_SHA256 = (
    "31419fb54be8292dd1b7ecf82e23506889fa6b03eb8e7d29e19de90287546862"
)
V18_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V18.md"
V18_PROTOCOL_SHA256 = (
    "66c6f52ff50c57f4bd6c22cdb13a55a1bfe41982238c5e7742b069505e624abb"
)
V18_HISTORICAL_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-surface-v18-self-oracle-failures.json"
)
V18_HISTORICAL_FAILURE_SHA256 = (
    "62c6e06f91c0caa44b75ccbc3c9d7ff499412f4d243634bb3a5742ef386e40d6"
)

# These are independently reviewed V12 instruction identities. They are never
# opened by a source-only control or Python reference. The candidate path must
# authenticate the finally published exact files and all three real retry
# reports before any candidate can be imported.
V12_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v12.py"
V12_SOURCE_SHA256 = (
    "81a519fa4890d5a7f6901d58c9154711be116fd7de4b081c0c052d64db481b3f"
)
V12_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V12.md"
V12_PROTOCOL_SHA256 = (
    "f74ccaf19f836f801de34aaf3228f9bcd14aabe88032ebee4dbe886247ec6b40"
)
V12_RETRY_SCHEMA = (
    "rebar-postfinal-current-build-proofs-v12-qualified-deep-retry-"
    "durable-proof"
)

FAMILIES = v18.FAMILIES
CONTRACT_NAMES = v18.CONTRACT_NAMES
V11_EDGE_ARCHIVE_RELATIVES = v18.V11_EDGE_ARCHIVE_RELATIVES
V11_EDGE_PROOF_RELATIVES = v18.V11_EDGE_PROOF_RELATIVES
V11_DEEP_ARCHIVE_RELATIVES = v18.V11_DEEP_ARCHIVE_RELATIVES
V11_DEEP_PROOF_RELATIVES = v18.V11_DEEP_PROOF_RELATIVES
V12_DEEP_RETRY_PROOF_RELATIVES = {
    family: (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-"
        + CONTRACT_NAMES[family]
        + "-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json"
    )
    for family in FAMILIES
}

MATRIX_SHA256 = v18.MATRIX_SHA256
STIMULUS_SHA256 = v18.STIMULUS_SHA256
EXPECTED_CASES = v18.EXPECTED_CASES
EXPECTED_COHORTS = v18.EXPECTED_COHORTS
EXPECTED_ADDITIONAL_CASES = v18.EXPECTED_ADDITIONAL_CASES
EXPECTED_LOCALE_CASES = v18.EXPECTED_LOCALE_CASES
EXPECTED_LOCALE_TRANSITIONS = v18.EXPECTED_LOCALE_TRANSITIONS

MAX_SOURCE_BYTES = v18.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = v18.MAX_REPORT_BYTES
MAX_ARCHIVE_BYTES = v18.MAX_ARCHIVE_BYTES
MAX_WORKER_BYTES = v18.MAX_WORKER_BYTES
MAX_NORMALIZATION_NODES = 200_000

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-surface-v19-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-public-surface-v19-all.json"
)
ALL_CANDIDATE_FAILURE_RELATIVE = (
    "candidates/evidence/python-re-public-surface-v19-all-failures.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-public-surface-v19-"
        + family + "-failures.json"
    )
    for family in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    ALL_CANDIDATE_FAILURE_RELATIVE,
    *CANDIDATE_FAILURE_RELATIVES.values(),
})

PRELOAD_MARKER = v18.PRELOAD_MARKER
AFTER_GUARD_MARKER = v18.AFTER_GUARD_MARKER
OWNER_RECORD_MARKER = v18.OWNER_RECORD_MARKER
PRELOAD_INJECTION = (
    "# BEGIN FROZEN V19 PRELOAD BEFORE CACHED-MATCHER POISON\n"
    "import os as _rebar19_os\n"
    "import json as _rebar19_json\n"
    "import importlib as _rebar19_importlib\n"
    "_rebar19_configuration = _rebar19_json.loads(\n"
    "    _rebar19_os.environ[\"REBAR_PUBLIC_SURFACE_V19_CONTEXT\"]\n"
    ")\n"
    "if any(_rebar19_name in sys.modules for _rebar19_name in (\n"
    "    \"candidates.rust_candidate\", \"candidates.vm_candidate\",\n"
    "    \"candidates.zig_candidate\",\n"
    ")):\n"
    "    raise RuntimeError(\"a candidate loaded before the V10 guard\")\n"
    "_rebar19_surface = _rebar19_importlib.import_module(\n"
    "    \"tools.python_re_public_surface_oracle_stage19\"\n"
    ")\n"
    "_rebar19_surface.verify_embedded_configuration(_rebar19_configuration)\n"
    "# END FROZEN V19 PRELOAD BEFORE CACHED-MATCHER POISON\n"
)
OBSERVATION_INJECTION = (
    "# BEGIN FROZEN V19 MATCHING INSIDE THE LIVE V10 GUARD\n"
    "_rebar19_candidate_name = (\n"
    "    \"candidates.\" + _rebar19_configuration[\"family\"] + \"_candidate\"\n"
    ")\n"
    "_rebar19_candidate = sys.modules.get(_rebar19_candidate_name)\n"
    "if _rebar19_candidate is None:\n"
    "    raise RuntimeError(\"the live guarded candidate was not imported\")\n"
    "if getattr(_rebar19_candidate, \"__name__\", None) != "
    "_rebar19_candidate_name:\n"
    "    raise RuntimeError(\"the live guarded candidate was substituted\")\n"
    "try:\n"
    "    _rebar19_public_observation = "
    "_rebar19_surface.guarded_public_records(\n"
    "        _rebar19_candidate, _rebar19_configuration,\n"
    "    )\n"
    "except BaseException as _rebar19_actual_failure:\n"
    "    _rebar19_failure = _rebar19_surface.guarded_failure_document(\n"
    "        _rebar19_configuration[\"family\"], "
    "_rebar19_actual_failure,\n"
    "    )\n"
    "    sys.stderr.write(_rebar19_surface.canonical(\n"
    "        _rebar19_failure\n"
    "    ).decode(\"ascii\") + \"\\n\")\n"
    "    raise\n"
    "# END FROZEN V19 MATCHING INSIDE THE LIVE V10 GUARD\n"
)
OWNER_RECORD_INJECTION = (
    '    "rebar_v19_guarded_public_surface": '
    '_rebar19_public_observation,\n'
)

_FROZEN_V17_NORMALIZE = v17.normalize


class PublicSurfaceV19Error(v17.PublicSurfaceError):
    """A genuine public observation, frozen owner, or proof did not pass."""


class PublicSurfaceV19WorkerFailure(PublicSurfaceV19Error):
    """Preserve the real role, complete streams, and actual partial rows."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


class _NormalizedEnvelope(dict):
    """Private identity marker; an ordinary lookalike dict is never trusted."""

    __slots__ = ("__weakref__",)


_AUTHENTIC_NORMALIZED_ENVELOPES: weakref.WeakValueDictionary[
    int, _NormalizedEnvelope
] = weakref.WeakValueDictionary()


def _new_normalized_envelope(**fields: Any) -> _NormalizedEnvelope:
    """Record the precise identity created by this normalizer's factory."""
    actual = _NormalizedEnvelope(fields)
    _AUTHENTIC_NORMALIZED_ENVELOPES[id(actual)] = actual
    return actual


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicSurfaceV19Error(message)


def canonical(value: Any) -> bytes:
    return v17.canonical(value)


def digest(value: Any) -> str:
    return v17.digest(value)


def valid_sha256(value: Any) -> bool:
    return v17.valid_sha256(value)


def normalize(value: Any, *, depth: int = 0) -> Any:
    """Iteratively encode real structure; reference only real shared objects.

    V17 intentionally calls its normalizer more than once for a single public
    observation. Only an envelope actually made by this private implementation
    is idempotent; a genuine user mapping with identical keys remains a mapping.
    No Python object address, recursion limit, or traversal guess is exposed.
    """
    require(type(depth) is int and depth >= 0,
            "a public normalization depth must be a nonnegative integer")
    root: list[Any] = [None]
    pending: list[tuple[str, Any, Any, Any]] = [("visit", value, root, 0)]
    seen: dict[int, tuple[int, Any]] = {}
    visited = 0

    def assign(container: Any, key: Any, actual: Any) -> None:
        container[key] = actual

    while pending:
        operation, current, container, key = pending.pop()
        if operation == "sort-mapping":
            current.sort(key=lambda pair: canonical(pair[0]))
            continue
        if operation == "sort-set":
            current.sort(key=canonical)
            continue

        visited += 1
        require(visited <= MAX_NORMALIZATION_NODES,
                "a public observation exceeds its explicit finite node budget")

        if (type(current) is _NormalizedEnvelope
                and _AUTHENTIC_NORMALIZED_ENVELOPES.get(id(current))
                is current):
            assign(container, key, current)
            continue
        if current is None or type(current) in (bool, int, str):
            assign(container, key, current)
            continue
        if type(current) is float:
            assign(container, key,
                   _new_normalized_envelope(kind="float", hex=current.hex()))
            continue
        if isinstance(current, (bytes, bytearray)):
            assign(container, key, _new_normalized_envelope(
                kind=type(current).__name__, hex=bytes(current).hex(),
            ))
            continue
        if isinstance(current, enum.IntFlag):
            assign(container, key, _new_normalized_envelope(
                kind="intflag",
                type=type(current).__name__,
                value=int(current),
                name=current.name,
                repr=repr(current),
            ))
            continue
        if isinstance(current, types.GenericAlias):
            assign(container, key, _new_normalized_envelope(
                kind="generic-alias",
                origin=getattr(current.__origin__, "__name__", None),
                args=[
                    getattr(item, "__name__", repr(item))
                    for item in current.__args__
                ],
                parameters=[repr(item) for item in current.__parameters__],
            ))
            continue
        if isinstance(current, type):
            assign(container, key, _new_normalized_envelope(
                kind="type", name=current.__name__,
            ))
            continue

        if not isinstance(
            current,
            (BaseException, Mapping, tuple, list, set, frozenset, memoryview),
        ):
            assign(container, key, _new_normalized_envelope(
                kind="public-object", type=type(current).__name__,
            ))
            continue

        object_key = id(current)
        prior = seen.get(object_key)
        if prior is not None and prior[1] is current:
            assign(container, key, _new_normalized_envelope(
                kind="reference", index=prior[0],
            ))
            continue
        seen[object_key] = (len(seen), current)

        if isinstance(current, BaseException):
            result = _new_normalized_envelope(
                kind="exception",
                type=type(current).__name__,
                message=str(current),
                args=None,
                pattern=None,
                msg=None,
                pos=None,
                lineno=None,
                colno=None,
                cause=None,
            )
            assign(container, key, result)
            fields = (
                ("args", current.args),
                ("pattern", getattr(current, "pattern", None)),
                ("msg", getattr(current, "msg", None)),
                ("pos", getattr(current, "pos", None)),
                ("lineno", getattr(current, "lineno", None)),
                ("colno", getattr(current, "colno", None)),
                ("cause", current.__cause__),
            )
            for field, item in reversed(fields):
                pending.append(("visit", item, result, field))
            continue

        if isinstance(current, Mapping):
            pairs = list(current.items())
            pairs.sort(key=lambda pair: canonical(normalize(pair[0])))
            entries: list[list[Any]] = []
            result = _new_normalized_envelope(kind="mapping", items=entries)
            assign(container, key, result)
            pending.append(("sort-mapping", entries, None, None))
            prepared: list[tuple[Any, Any, list[Any]]] = []
            for actual_key, actual_value in pairs:
                entry: list[Any] = [None, None]
                entries.append(entry)
                prepared.append((actual_key, actual_value, entry))
            for actual_key, actual_value, entry in reversed(prepared):
                pending.append(("visit", actual_value, entry, 1))
                pending.append(("visit", actual_key, entry, 0))
            continue

        if isinstance(current, (tuple, list)):
            items: list[Any] = [None] * len(current)
            result = _new_normalized_envelope(
                kind=type(current).__name__, items=items,
            )
            assign(container, key, result)
            for index in reversed(range(len(current))):
                pending.append(("visit", current[index], items, index))
            continue

        if isinstance(current, (set, frozenset)):
            ordered = sorted(current, key=lambda item: canonical(normalize(item)))
            items = [None] * len(ordered)
            result = _new_normalized_envelope(
                kind=type(current).__name__, items=items,
            )
            assign(container, key, result)
            pending.append(("sort-set", items, None, None))
            for index in reversed(range(len(ordered))):
                pending.append(("visit", ordered[index], items, index))
            continue

        result = _new_normalized_envelope(
            kind="memoryview", format=current.format,
            shape=None, hex=current.tobytes().hex(),
        )
        assign(container, key, result)
        pending.append(("visit", current.shape, result, "shape"))

    return root[0]


@contextlib.contextmanager
def cycle_safe_normalization() -> Iterator[None]:
    """Reversibly install only the source-authenticated V17 normalization."""
    previous = v17.normalize
    require(previous is _FROZEN_V17_NORMALIZE or previous is normalize,
            "the immutable public evaluator's normalization was substituted")
    v17.normalize = normalize
    try:
        yield
    finally:
        v17.normalize = previous


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == str(v17.PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.abspath(v17.__file__) == str(ROOT / V17_SOURCE_RELATIVE)
        and os.path.abspath(v18.__file__) == str(ROOT / V18_SOURCE_RELATIVE)
        and v17.SCHEMA == "rebar-python-re-independent-public-surface-v17"
        and v18.SCHEMA == "rebar-python-re-guarded-durable-public-surface-v18"
        and v18.V17_SOURCE_SHA256 == V17_SOURCE_SHA256
        and v18.V17_PROTOCOL_SHA256 == V17_PROTOCOL_SHA256
        and v17.MATRIX_SHA256 == MATRIX_SHA256
        and v17.STIMULUS_SHA256 == STIMULUS_SHA256
        and v17.EXPECTED_CASES == EXPECTED_CASES
        and len(v17.COHORTS) == EXPECTED_COHORTS
        and tuple(FAMILIES) == ("rust", "vm", "zig")
        and v17.V5_REFERENCE_SHA256
        == "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916",
        "use the exact isolated CPython 3.14.6 and immutable V17/V18 contract",
    )


def authenticate_frozen_predecessors() -> None:
    verify_runtime()
    for relative, expected in (
        (V17_SOURCE_RELATIVE, V17_SOURCE_SHA256),
        (V17_PROTOCOL_RELATIVE, V17_PROTOCOL_SHA256),
        (V18_SOURCE_RELATIVE, V18_SOURCE_SHA256),
        (V18_PROTOCOL_RELATIVE, V18_PROTOCOL_SHA256),
    ):
        v17._read_bounded(relative, MAX_SOURCE_BYTES, expected=expected)


def safe_relative(relative: Any, *, outputs_only: bool = False) -> str:
    require(type(relative) is str, "an exact repository-relative path is required")
    path = PurePosixPath(relative)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in relative
        and "\x00" not in relative
        and path.as_posix() == relative
        and (not outputs_only or relative in APPROVED_OUTPUTS),
        "refusing an escaping, unapproved, reused, or historical evidence path",
    )
    return relative


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    safe_relative(relative)
    require(valid_sha256(expected),
            "an independently published exact SHA-256 is required")
    return v17._read_bounded(relative, maximum, expected=expected)


def strict_canonical(payload: bytes, label: str) -> dict[str, Any]:
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=v17._unique_json_pairs,
            parse_constant=lambda actual: (_ for _ in ()).throw(
                PublicSurfaceV19Error("a non-finite proof was forged: " + actual),
            ),
        )
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicSurfaceV19Error(
            "complete original canonical JSON is malformed: " + label,
        ) from error
    require(isinstance(document, dict)
            and payload in {canonical(document), canonical(document) + b"\n"},
            "complete independently retained canonical JSON changed: " + label)
    return document


def capture_complete_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_WORKER_BYTES,
            "an original worker stream must be complete bounded bytes")
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def restore_complete_stream(record: Any, *, label: str) -> bytes:
    require(
        isinstance(record, dict)
        and set(record) == {"bytes", "sha256", "complete", "base64"}
        and type(record.get("bytes")) is int
        and 0 <= record["bytes"] <= MAX_WORKER_BYTES
        and valid_sha256(record.get("sha256"))
        and record.get("complete") is True
        and type(record.get("base64")) is str,
        "an actual complete worker stream was omitted or forged: " + label,
    )
    try:
        payload = base64.b64decode(record["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError, base64.binascii.Error) as error:
        raise PublicSurfaceV19Error(
            "the actual original worker stream is invalid base64: " + label,
        ) from error
    require(
        len(payload) == record["bytes"]
        and hashlib.sha256(payload).hexdigest() == record["sha256"]
        and capture_complete_stream(payload) == record,
        "the exact complete original worker stream changed: " + label,
    )
    return payload


def validate_process_streams(
    process: Any,
    *,
    role: str,
    expected_document: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        isinstance(process, dict)
        and set(process) == {"role", "returncode", "stdout", "stderr"}
        and process.get("role") == role
        and type(process.get("returncode")) is int
        and process.get("returncode") == 0,
        "a real independently retained worker exited unsuccessfully",
    )
    stdout = restore_complete_stream(process.get("stdout"), label=role + " stdout")
    stderr = restore_complete_stream(process.get("stderr"), label=role + " stderr")
    require(stderr == b"", "a passing worker concealed actual stderr")
    require(strict_canonical(stdout, role + " complete stdout")
            == dict(expected_document),
            "the real full stdout and retained worker document disagree")
    return process


def build_matrix() -> list[dict[str, Any]]:
    matrix = v18.build_matrix()
    require(
        len(matrix) == EXPECTED_CASES
        and v17.validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
        == MATRIX_SHA256,
        "the immutable independently seeded 1,376-case matrix changed",
    )
    observed = v17.validate_stimuli(matrix, expected_sha256=STIMULUS_SHA256)
    require(
        observed.get("cases") == EXPECTED_CASES
        and observed.get("cohorts") == EXPECTED_COHORTS
        and observed.get("additional_cases") == EXPECTED_ADDITIONAL_CASES
        and observed.get("distinct_stimuli") == EXPECTED_CASES
        and observed.get("stimulus_sha256") == STIMULUS_SHA256,
        "an original public input, cohort, or actual stimulus was omitted",
    )
    return matrix


def validate_partial_records(
    records: Any,
    matrix: list[dict[str, Any]],
) -> dict[str, int]:
    require(isinstance(records, list) and len(records) <= EXPECTED_CASES,
            "actual complete-prefix public records must be retained")
    additional = 0
    returned_additional = 0
    raised_additional = 0
    locales = 0
    for expected, actual in zip(matrix, records, strict=False):
        stimulus = v17.build_stimulus(expected)
        outcome = actual.get("outcome") if isinstance(actual, dict) else None
        require(
            isinstance(actual, dict)
            and set(actual) == {"id", "cohort", "stimulus_sha256", "outcome"}
            and actual.get("id") == expected["id"]
            and actual.get("cohort") == expected["cohort"]
            and actual.get("stimulus_sha256") == digest(stimulus)
            and isinstance(outcome, dict)
            and (
                (outcome.get("status") == "return"
                 and set(outcome) == {"status", "value"})
                or (outcome.get("status") == "raise"
                    and set(outcome) == {"status", "exception"}
                    and isinstance(outcome.get("exception"), dict)
                    and outcome["exception"].get("kind") == "exception")
            ),
            "an actual public record, expected exception, or exact seed changed",
        )
        if expected["cohort"] in v17.ADDITIONAL_COHORTS:
            additional += 1
            if outcome["status"] == "return":
                returned_additional += 1
            else:
                raised_additional += 1
        if expected["cohort"] in {
            "real-locale-switch-on-compiled-bytes",
            "real-locale-invalid-flags-and-cache",
        }:
            v17._validate_locale_case(actual)
            locales += 1
    return {
        "additional_cases": additional,
        "returned_additional_cases": returned_additional,
        "raised_additional_cases": raised_additional,
        "real_locale_cases": locales,
    }


def validate_public_records(records: Any) -> str:
    matrix = build_matrix()
    require(isinstance(records, list) and len(records) == EXPECTED_CASES,
            "all 1,376 original genuine public observations are required")
    counts = validate_partial_records(records, matrix)
    require(
        counts["additional_cases"] == EXPECTED_ADDITIONAL_CASES
        and counts["returned_additional_cases"]
        + counts["raised_additional_cases"] == EXPECTED_ADDITIONAL_CASES
        and counts["real_locale_cases"] == EXPECTED_LOCALE_CASES,
        "all original seeded exceptions and genuine locale cases are mandatory",
    )
    return digest(records)


def _locale_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    return validate_partial_records(records, build_matrix())


def _locale_names(options: argparse.Namespace) -> dict[str, str]:
    require(
        type(options.iso8859_1_locale) is str
        and bool(options.iso8859_1_locale)
        and type(options.utf8_locale) is str
        and bool(options.utf8_locale)
        and options.iso8859_1_locale != options.utf8_locale,
        "BLOCKED: provision genuinely distinct fresh ISO-8859-1 and UTF-8 locales",
    )
    return {"iso8859_1": options.iso8859_1_locale,
            "utf8": options.utf8_locale}


def verify_embedded_configuration(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and set(value) == {
            "schema", "family", "source_sha256", "protocol_sha256",
            "v17_source_sha256", "v17_protocol_sha256",
            "v18_source_sha256", "v18_protocol_sha256",
            "matrix_sha256", "stimulus_sha256", "cases",
            "iso8859_1_locale", "utf8_locale", "expected_native_sha256",
        }
        and value.get("schema") == SCHEMA + "-embedded-configuration"
        and value.get("family") in FAMILIES
        and valid_sha256(value.get("source_sha256"))
        and valid_sha256(value.get("protocol_sha256"))
        and value.get("v17_source_sha256") == V17_SOURCE_SHA256
        and value.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and value.get("v18_source_sha256") == V18_SOURCE_SHA256
        and value.get("v18_protocol_sha256") == V18_PROTOCOL_SHA256
        and value.get("matrix_sha256") == MATRIX_SHA256
        and value.get("stimulus_sha256") == STIMULUS_SHA256
        and value.get("cases") == EXPECTED_CASES
        and type(value.get("iso8859_1_locale")) is str
        and bool(value["iso8859_1_locale"])
        and type(value.get("utf8_locale")) is str
        and bool(value["utf8_locale"])
        and value["iso8859_1_locale"] != value["utf8_locale"]
        and isinstance(value.get("expected_native_sha256"), dict)
        and bool(value["expected_native_sha256"])
        and all(
            type(relative) is str and valid_sha256(actual)
            for relative, actual in value["expected_native_sha256"].items()
        ),
        "the exact same-process, frozen live-native-owner context was forged",
    )
    return dict(value)


def compose_guarded_owner(
    owner_source: str,
    *,
    owner_source_sha256: str,
) -> tuple[str, str]:
    require(
        type(owner_source) is str
        and valid_sha256(owner_source_sha256)
        and hashlib.sha256(owner_source.encode("utf-8")).hexdigest()
        == owner_source_sha256,
        "the exact complete immutable V10 native owner worker was substituted",
    )
    for marker, label in (
        (PRELOAD_MARKER, "before the original cached-matcher poison"),
        (AFTER_GUARD_MARKER, "inside the genuine original live guard"),
        (OWNER_RECORD_MARKER, "inside the unchanged complete owner record"),
    ):
        require(owner_source.count(marker) == 1,
                "the genuine native worker has no unique insertion point " + label)
    require(owner_source.index(PRELOAD_MARKER)
            < owner_source.index(AFTER_GUARD_MARKER)
            < owner_source.index(OWNER_RECORD_MARKER),
            "the genuine native guard and owner-observation order changed")
    try:
        original_tree = ast.parse(owner_source)
    except SyntaxError as error:
        raise PublicSurfaceV19Error(
            "the exact genuine original native-owner worker is invalid Python",
        ) from error
    composed = owner_source.replace(
        PRELOAD_MARKER, PRELOAD_INJECTION + PRELOAD_MARKER, 1,
    ).replace(
        AFTER_GUARD_MARKER, OBSERVATION_INJECTION + AFTER_GUARD_MARKER, 1,
    ).replace(
        OWNER_RECORD_MARKER, OWNER_RECORD_INJECTION + OWNER_RECORD_MARKER, 1,
    )
    try:
        composed_tree = ast.parse(composed)
    except SyntaxError as error:
        raise PublicSurfaceV19Error(
            "the precisely composed same-process guard is invalid Python",
        ) from error
    original_imports = {
        alias.name
        for node in ast.walk(original_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    actual_imports = {
        alias.name
        for node in ast.walk(composed_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    require(
        actual_imports - original_imports <= {"os", "json", "importlib"}
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in actual_imports - original_imports
        )
        and composed.count(PRELOAD_INJECTION) == 1
        and composed.count(OBSERVATION_INJECTION) == 1
        and composed.count(OWNER_RECORD_INJECTION) == 1
        and composed.count(AFTER_GUARD_MARKER) == 1
        and composed.index(PRELOAD_INJECTION) < composed.index(PRELOAD_MARKER)
        and composed.index(OBSERVATION_INJECTION)
        < composed.index(AFTER_GUARD_MARKER)
        and composed.index(OWNER_RECORD_INJECTION)
        < composed.index(OWNER_RECORD_MARKER),
        "public matching did not occur exactly once inside the original guard",
    )
    restored = composed.replace(
        PRELOAD_INJECTION + PRELOAD_MARKER, PRELOAD_MARKER, 1,
    ).replace(
        OBSERVATION_INJECTION + AFTER_GUARD_MARKER, AFTER_GUARD_MARKER, 1,
    ).replace(
        OWNER_RECORD_INJECTION + OWNER_RECORD_MARKER, OWNER_RECORD_MARKER, 1,
    )
    require(restored == owner_source
            and hashlib.sha256(restored.encode("utf-8")).hexdigest()
            == owner_source_sha256,
            "the original frozen guard or actual native-owner source changed")
    return composed, hashlib.sha256(composed.encode("utf-8")).hexdigest()


def _error_details(error: BaseException) -> dict[str, Any]:
    return {
        "actual_error": normalize(error),
        "traceback": "".join(traceback.format_exception(
            type(error), error, error.__traceback__,
        )),
    }


def _timeout_failure_details(
    role: str,
    error: subprocess.TimeoutExpired,
    *,
    owner_before: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Preserve observed timeout bytes without pretending a process finished."""
    details: dict[str, Any] = {
        "role": role,
        "timed_out": True,
        "timeout_seconds": error.timeout,
        "returncode": None,
        **_error_details(error),
    }
    for label in ("stdout", "stderr"):
        raw = getattr(error, label, None)
        if raw is None:
            details[label] = None
            continue
        require(type(raw) is bytes,
                "a timed-out binary worker substituted its observed " + label)
        observed = capture_complete_stream(raw)
        observed["complete"] = False
        observed["captured_before_timeout"] = True
        details[label] = observed
    if owner_before is not None:
        details["owner_before"] = dict(owner_before)
    return details


def guarded_failure_document(family: str, error: BaseException) -> dict[str, Any]:
    details = (
        dict(error.details)
        if isinstance(error, PublicSurfaceV19WorkerFailure)
        else {}
    )
    return {
        "schema": SCHEMA + "-embedded-public-failure",
        "status": "FAIL",
        "family": family,
        "actual_failure_details": details,
        **_error_details(error),
        "benchmark_or_timing_executed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
    }


def _validate_locale_preflight(value: Any) -> None:
    require(
        isinstance(value, dict)
        and value.get("iso8859_1_codeset") in {"iso88591", "latin1"}
        and value.get("utf8_codeset") == "utf8"
        and value.get("ctype_restored") is True
        and value.get("locale_path_unchanged") is True,
        "both actual fresh locale encodings and complete restoration are required",
    )


def guarded_public_records(
    module: Any,
    configuration: Mapping[str, Any],
) -> dict[str, Any]:
    settings = verify_embedded_configuration(configuration)
    family = settings["family"]
    expected_name = "candidates." + family + "_candidate"
    require(getattr(module, "__name__", None) == expected_name
            and sys.modules.get(expected_name) is module,
            "the public module must be the candidate already imported by V10")
    authenticate_frozen_predecessors()
    read_frozen(SOURCE_RELATIVE, settings["source_sha256"], MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, settings["protocol_sha256"], MAX_SOURCE_BYTES)
    matrix = build_matrix()
    locale_names = {
        "iso8859_1": settings["iso8859_1_locale"],
        "utf8": settings["utf8_locale"],
    }
    records: list[dict[str, Any]] = []
    active: str | None = None
    locale_preflight: dict[str, Any] | None = None
    failure_stage = "preflight"
    try:
        locale_preflight = v17._preflight_real_locales(locale_names)
        _validate_locale_preflight(locale_preflight)
        with cycle_safe_normalization():
            for row in matrix:
                failure_stage = "case"
                active = row["id"]
                record = v17.evaluate_case(module, row, locale_names=locale_names)
                if row["cohort"] in {
                    "real-locale-switch-on-compiled-bytes",
                    "real-locale-invalid-flags-and-cache",
                }:
                    v17._validate_locale_case(record)
                records.append(record)
                active = None
        failure_stage = "postflight"
        counts = _locale_counts(records)
        return {
            "schema": SCHEMA + "-embedded-public-records",
            "status": "PASS",
            "family": family,
            "candidate_module": expected_name,
            "source_sha256": settings["source_sha256"],
            "protocol_sha256": settings["protocol_sha256"],
            "v17_source_sha256": V17_SOURCE_SHA256,
            "v17_protocol_sha256": V17_PROTOCOL_SHA256,
            "v18_source_sha256": V18_SOURCE_SHA256,
            "v18_protocol_sha256": V18_PROTOCOL_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cases": EXPECTED_CASES,
            "retained_additional_cases": counts["additional_cases"],
            "returned_additional_cases": counts["returned_additional_cases"],
            "raised_additional_cases": counts["raised_additional_cases"],
            "successful_real_locale_cases": counts["real_locale_cases"],
            "real_locale_transition_count": EXPECTED_LOCALE_TRANSITIONS,
            "locale_preflight": locale_preflight,
            "expected_native_sha256": settings["expected_native_sha256"],
            "records": records,
            "record_sha256": validate_public_records(records),
            "matched_inside_live_v10_owner_guard": True,
            "candidate_imported_by_frozen_owner_only": True,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
    except BaseException as error:
        raise PublicSurfaceV19WorkerFailure(
            family,
            "the genuine guarded public candidate failed inside its native owner",
            {
                "completed_records": records,
                "completed_count": len(records),
                "failure_stage": failure_stage,
                "active_case": active,
                "locale_preflight": locale_preflight,
                **_error_details(error),
            },
        ) from error


def validate_embedded_records(
    document: Any,
    *,
    family: str,
    source_sha256: str,
    protocol_sha256: str,
    expected_native: Mapping[str, str],
    baseline: list[dict[str, Any]],
) -> dict[str, Any]:
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-embedded-public-records"
        and document.get("status") == "PASS"
        and document.get("family") == family
        and document.get("candidate_module")
        == "candidates." + family + "_candidate"
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("v17_source_sha256") == V17_SOURCE_SHA256
        and document.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and document.get("v18_source_sha256") == V18_SOURCE_SHA256
        and document.get("v18_protocol_sha256") == V18_PROTOCOL_SHA256
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("stimulus_sha256") == STIMULUS_SHA256
        and document.get("cases") == EXPECTED_CASES
        and document.get("retained_additional_cases")
        == EXPECTED_ADDITIONAL_CASES
        and type(document.get("returned_additional_cases")) is int
        and type(document.get("raised_additional_cases")) is int
        and document["returned_additional_cases"]
        + document["raised_additional_cases"] == EXPECTED_ADDITIONAL_CASES
        and document.get("successful_real_locale_cases") == EXPECTED_LOCALE_CASES
        and document.get("real_locale_transition_count")
        == EXPECTED_LOCALE_TRANSITIONS
        and document.get("expected_native_sha256") == dict(expected_native)
        and document.get("matched_inside_live_v10_owner_guard") is True
        and document.get("candidate_imported_by_frozen_owner_only") is True
        and document.get("performance_fixtures_read") == 0
        and document.get("holdout_cases_read") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance") == "NOT MEASURED",
        "the actual complete same-process live native guard was forged",
    )
    _validate_locale_preflight(document.get("locale_preflight"))
    records = document.get("records")
    require(validate_public_records(records) == document.get("record_sha256"),
            "a complete actual guarded public row was omitted or changed")
    counts = _locale_counts(records)
    require(counts["returned_additional_cases"]
            == document["returned_additional_cases"]
            and counts["raised_additional_cases"]
            == document["raised_additional_cases"]
            and records == baseline,
            "the guarded native candidate differs from both full Python oracles")
    return document


def authenticate_reference_prerequisites(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    verify_runtime()
    read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    authenticate_frozen_predecessors()
    baseline = v17.authenticate_reference(V17_SOURCE_SHA256, V17_PROTOCOL_SHA256)
    require(
        baseline.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and baseline.get("original_matrix_sha256") == v17.ORIGINAL_MATRIX_SHA256
        and baseline.get("original_public_methods") == 152
        and baseline.get("original_passed") == 151
        and baseline.get("original_named_private_skips") == 1
        and baseline.get("candidate_audits_read") == 0
        and baseline.get("candidate_proofs_read") == 0
        and baseline.get("candidate_imports") == 0,
        "the original candidate-free complete upstream Python baseline failed",
    )
    build_matrix()
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v18_source_sha256": V18_SOURCE_SHA256,
        "v18_protocol_sha256": V18_PROTOCOL_SHA256,
        "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
        "original_public_methods": 152,
        "original_passed": 151,
        "original_named_private_debug_skips": 1,
        "candidate_audits_read": 0,
        "candidate_proofs_read": 0,
        "candidate_imports": 0,
        "v12_sources_read": 0,
        "current_graph_candidate_qualification":
            CURRENT_GRAPH_CANDIDATE_QUALIFICATION,
        "candidate_evidence_current": CURRENT_GRAPH_CANDIDATE_EVIDENCE,
        "current_graph_candidate_qualification_reason":
            CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
        "historical_failure_qualifies_current_build": False,
        "performance": "NOT MEASURED",
    }


def _reference_failure_document(
    *,
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locale_names: Mapping[str, str],
    locale_preflight: Mapping[str, Any] | None,
    completed_records: list[dict[str, Any]],
    failure_stage: str,
    active_case: str | None,
    error: BaseException,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-reference-worker",
        "status": "FAIL",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v18_source_sha256": V18_SOURCE_SHA256,
        "v18_protocol_sha256": V18_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "expected_cases": EXPECTED_CASES,
        "requested_locales": dict(locale_names),
        "locale_preflight": (
            dict(locale_preflight) if locale_preflight is not None else None
        ),
        "completed_records": completed_records,
        "completed_count": len(completed_records),
        "failure_stage": failure_stage,
        "active_case": active_case,
        **_error_details(error),
        "guard": {
            "baseline_only": True,
            "candidate_imported": any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
        },
        "candidate_audits_read": 0,
        "candidate_proofs_read": 0,
        "v12_sources_read": 0,
        "current_graph_candidate_qualification":
            CURRENT_GRAPH_CANDIDATE_QUALIFICATION,
        "candidate_evidence_current": CURRENT_GRAPH_CANDIDATE_EVIDENCE,
        "current_graph_candidate_qualification_reason":
            CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def validate_reference_failure(
    document: Any,
    *,
    role: str,
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-reference-worker"
        and document.get("status") == "FAIL"
        and document.get("role") == role
        and document.get("python") == "3.14.6"
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("v17_source_sha256") == V17_SOURCE_SHA256
        and document.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and document.get("v18_source_sha256") == V18_SOURCE_SHA256
        and document.get("v18_protocol_sha256") == V18_PROTOCOL_SHA256
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("stimulus_sha256") == STIMULUS_SHA256
        and document.get("expected_cases") == EXPECTED_CASES
        and isinstance(document.get("requested_locales"), dict)
        and set(document["requested_locales"]) == {"iso8859_1", "utf8"}
        and type(document["requested_locales"].get("iso8859_1")) is str
        and bool(document["requested_locales"]["iso8859_1"])
        and type(document["requested_locales"].get("utf8")) is str
        and bool(document["requested_locales"]["utf8"])
        and document["requested_locales"]["iso8859_1"]
        != document["requested_locales"]["utf8"]
        and isinstance(document.get("completed_records"), list)
        and type(document.get("completed_count")) is int
        and document["completed_count"] == len(document["completed_records"])
        and 0 <= document["completed_count"] <= EXPECTED_CASES
        and document.get("failure_stage") in {"preflight", "case", "postflight"}
        and isinstance(document.get("actual_error"), dict)
        and document["actual_error"].get("kind") == "exception"
        and type(document.get("traceback")) is str
        and bool(document["traceback"])
        and document.get("guard") == {
            "baseline_only": True, "candidate_imported": False,
        }
        and document.get("candidate_audits_read") == 0
        and document.get("candidate_proofs_read") == 0
        and document.get("v12_sources_read") == 0
        and document.get("current_graph_candidate_qualification")
        == CURRENT_GRAPH_CANDIDATE_QUALIFICATION
        and document.get("candidate_evidence_current")
        == CURRENT_GRAPH_CANDIDATE_EVIDENCE
        and document.get("current_graph_candidate_qualification_reason")
        == CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON
        and document.get("holdout_cases_read") == 0
        and document.get("performance_fixtures_read") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance") == "NOT MEASURED",
        "an actual Python reference's complete inner failure was forged",
    )
    matrix = build_matrix()
    validate_partial_records(document["completed_records"], matrix)
    count = document["completed_count"]
    expected_active = matrix[count]["id"] if count < EXPECTED_CASES else None
    stage = document["failure_stage"]
    require(
        (stage == "preflight"
         and count == 0
         and document.get("active_case") is None)
        or (stage == "case"
            and count < EXPECTED_CASES
            and document.get("active_case") == expected_active)
        or (stage == "postflight"
            and count == EXPECTED_CASES
            and document.get("active_case") is None),
        "the actual failing public row, complete prefix, or failure stage "
        "was omitted or substituted",
    )
    observed = document.get("locale_preflight")
    if stage in {"case", "postflight"}:
        _validate_locale_preflight(observed)
    elif observed is not None:
        _validate_locale_preflight(observed)
    return document


def _reference_worker_document(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locale_names: Mapping[str, str],
) -> dict[str, Any]:
    verify_runtime()
    require(role in {"reference_a", "reference_b"},
            "a candidate cannot execute in a real Python reference worker")
    read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    authenticate_frozen_predecessors()
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "an actual separately started Python reference imported a candidate")
    records: list[dict[str, Any]] = []
    active: str | None = None
    preflight: dict[str, Any] | None = None
    failure_stage = "preflight"
    try:
        preflight = v17._preflight_real_locales(locale_names)
        _validate_locale_preflight(preflight)
        module = importlib.import_module("re")
        require(module.__name__ == "re",
                "the real pinned CPython standard-library reference changed")
        with cycle_safe_normalization():
            for row in build_matrix():
                failure_stage = "case"
                active = row["id"]
                record = v17.evaluate_case(module, row, locale_names=locale_names)
                if row["cohort"] in {
                    "real-locale-switch-on-compiled-bytes",
                    "real-locale-invalid-flags-and-cache",
                }:
                    v17._validate_locale_case(record)
                records.append(record)
                active = None
        failure_stage = "postflight"
        counts = _locale_counts(records)
        result = {
            "schema": SCHEMA + "-reference-worker",
            "status": "PASS",
            "role": role,
            "python": "3.14.6",
            "source_sha256": source_sha256,
            "protocol_sha256": protocol_sha256,
            "v17_source_sha256": V17_SOURCE_SHA256,
            "v17_protocol_sha256": V17_PROTOCOL_SHA256,
            "v18_source_sha256": V18_SOURCE_SHA256,
            "v18_protocol_sha256": V18_PROTOCOL_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cases": EXPECTED_CASES,
            "retained_additional_cases": counts["additional_cases"],
            "returned_additional_cases": counts["returned_additional_cases"],
            "raised_additional_cases": counts["raised_additional_cases"],
            "successful_real_locale_cases": counts["real_locale_cases"],
            "real_locale_transition_count": EXPECTED_LOCALE_TRANSITIONS,
            "locale_preflight": preflight,
            "records": records,
            "record_sha256": validate_public_records(records),
            "guard": {"baseline_only": True, "candidate_imported": False},
            "candidate_audits_read": 0,
            "candidate_proofs_read": 0,
            "v12_sources_read": 0,
            "current_graph_candidate_qualification":
                CURRENT_GRAPH_CANDIDATE_QUALIFICATION,
            "candidate_evidence_current": CURRENT_GRAPH_CANDIDATE_EVIDENCE,
            "current_graph_candidate_qualification_reason":
                CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
            "subinterpreter_coverage": "NOT RUN",
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        return result
    except BaseException as error:
        return _reference_failure_document(
            role=role,
            source_sha256=source_sha256,
            protocol_sha256=protocol_sha256,
            locale_names=locale_names,
            locale_preflight=preflight,
            completed_records=records,
            failure_stage=failure_stage,
            active_case=active,
            error=error,
        )


def validate_reference_worker(
    document: Any,
    *,
    role: str,
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-reference-worker"
        and document.get("status") == "PASS"
        and document.get("role") == role
        and document.get("python") == "3.14.6"
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("v17_source_sha256") == V17_SOURCE_SHA256
        and document.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and document.get("v18_source_sha256") == V18_SOURCE_SHA256
        and document.get("v18_protocol_sha256") == V18_PROTOCOL_SHA256
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("stimulus_sha256") == STIMULUS_SHA256
        and document.get("cases") == EXPECTED_CASES
        and document.get("retained_additional_cases")
        == EXPECTED_ADDITIONAL_CASES
        and type(document.get("returned_additional_cases")) is int
        and type(document.get("raised_additional_cases")) is int
        and document["returned_additional_cases"]
        + document["raised_additional_cases"] == EXPECTED_ADDITIONAL_CASES
        and document.get("successful_real_locale_cases") == EXPECTED_LOCALE_CASES
        and document.get("real_locale_transition_count")
        == EXPECTED_LOCALE_TRANSITIONS
        and document.get("guard") == {
            "baseline_only": True, "candidate_imported": False,
        }
        and document.get("candidate_audits_read") == 0
        and document.get("candidate_proofs_read") == 0
        and document.get("v12_sources_read") == 0
        and document.get("current_graph_candidate_qualification")
        == CURRENT_GRAPH_CANDIDATE_QUALIFICATION
        and document.get("candidate_evidence_current")
        == CURRENT_GRAPH_CANDIDATE_EVIDENCE
        and document.get("current_graph_candidate_qualification_reason")
        == CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON
        and document.get("subinterpreter_coverage") == "NOT RUN"
        and document.get("holdout_cases_read") == 0
        and document.get("performance_fixtures_read") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance") == "NOT MEASURED",
        "the complete real candidate-free isolated Python reference was forged",
    )
    _validate_locale_preflight(document.get("locale_preflight"))
    records = document.get("records")
    require(validate_public_records(records) == document.get("record_sha256"),
            "a real original Python reference record was concealed")
    counts = _locale_counts(records)
    require(counts["returned_additional_cases"]
            == document["returned_additional_cases"]
            and counts["raised_additional_cases"]
            == document["raised_additional_cases"],
            "actual seeded reference exceptions were suppressed or relabelled")
    return document


def _run_reference_worker(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = [
        str(v17.PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--reference-worker", role,
        "--source-sha256", source_sha256,
        "--protocol-sha256", protocol_sha256,
        "--iso8859-1-locale", locales["iso8859_1"],
        "--utf8-locale", locales["utf8"],
    ]
    try:
        process = subprocess.run(
            command,
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3_600,
        )
    except subprocess.TimeoutExpired as error:
        raise PublicSurfaceV19WorkerFailure(
            role,
            "the genuine independently started Python reference timed out",
            _timeout_failure_details(role, error),
        ) from error
    except (OSError, subprocess.SubprocessError) as error:
        raise PublicSurfaceV19WorkerFailure(
            role,
            "an actual separately started Python reference crashed or timed out",
            {"role": role, **_error_details(error)},
        ) from error

    require(len(process.stdout) <= MAX_WORKER_BYTES
            and len(process.stderr) <= MAX_WORKER_BYTES,
            "the complete actual Python worker streams exceed their safe bound")
    retained_process = {
        "role": role,
        "returncode": process.returncode,
        "stdout": capture_complete_stream(process.stdout),
        "stderr": capture_complete_stream(process.stderr),
    }
    if process.returncode != 0 or process.stderr:
        details: dict[str, Any] = {
            "role": role,
            "returncode": process.returncode,
            "stdout": retained_process["stdout"],
            "stderr": retained_process["stderr"],
            "complete_original_worker_streams": retained_process,
        }
        if process.stdout:
            try:
                inner = strict_canonical(process.stdout, role + " actual failure")
                details["actual_worker_document"] = validate_reference_failure(
                    inner,
                    role=role,
                    source_sha256=source_sha256,
                    protocol_sha256=protocol_sha256,
                )
                details["completed_records"] = inner["completed_records"]
                details["completed_count"] = inner["completed_count"]
                details["failure_stage"] = inner["failure_stage"]
                details["active_case"] = inner["active_case"]
                details["actual_error"] = inner["actual_error"]
                details["traceback"] = inner["traceback"]
            except (
                PublicSurfaceV19Error, v17.PublicSurfaceError,
                v18.PublicSurfaceV18Error, ValueError, TypeError, KeyError,
            ) as decode_error:
                details["actual_failure_decode_error"] = _error_details(
                    decode_error,
                )
        raise PublicSurfaceV19WorkerFailure(
            role,
            "a genuine isolated Python reference returned an actual failure",
            details,
        )

    observed: dict[str, Any] | None = None
    try:
        observed = strict_canonical(
            process.stdout, role + " complete original stdout",
        )
        validated = validate_reference_worker(
            observed,
            role=role,
            source_sha256=source_sha256,
            protocol_sha256=protocol_sha256,
        )
        validate_process_streams(retained_process, role=role,
                                 expected_document=validated)
    except BaseException as error:
        details = {
            "role": role,
            "returncode": process.returncode,
            "stdout": retained_process["stdout"],
            "stderr": retained_process["stderr"],
            "complete_original_worker_streams": retained_process,
            **_error_details(error),
        }
        if observed is not None:
            details["actual_unvalidated_worker_document"] = observed
        raise PublicSurfaceV19WorkerFailure(
            role,
            "the real complete Python worker result failed strict validation",
            details,
        ) from error
    return validated, retained_process


def _preflight_destinations(paths: tuple[str, ...]) -> None:
    require(len(paths) == len(set(paths)),
            "actual passing and failure outputs must be different")
    for relative in paths:
        path = ROOT / safe_relative(relative, outputs_only=True)
        require(
            path.parent.is_dir()
            and not path.parent.is_symlink()
            and path.resolve(strict=False) == path
            and not path.exists()
            and not path.is_symlink(),
            "refusing to replace, retry, or follow public evidence: " + relative,
        )


def exclusive_write(document: Mapping[str, Any], relative: str) -> str:
    path = ROOT / safe_relative(relative, outputs_only=True)
    payload = canonical(document) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "the entire original correctness report exceeds its safe bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        directory = os.open(path.parent, directory_flags)
    except OSError as error:
        raise PublicSurfaceV19Error(
            "refusing an unavailable, replaced, or symbolic evidence directory: "
            + relative,
        ) from error
    try:
        opened_directory = os.fstat(directory)
        current_directory = os.stat(path.parent, follow_symlinks=False)
        require(
            stat.S_ISDIR(opened_directory.st_mode)
            and stat.S_ISDIR(current_directory.st_mode)
            and (opened_directory.st_dev, opened_directory.st_ino)
            == (current_directory.st_dev, current_directory.st_ino),
            "the actual canonical evidence directory was exchanged or redirected",
        )
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(
                path.name, flags, 0o600, dir_fd=directory,
            )
        except OSError as error:
            raise PublicSurfaceV19Error(
                "refusing to overwrite, redirect, or retry actual public "
                "evidence: " + relative,
            ) from error
        try:
            remaining = memoryview(payload)
            while remaining:
                count = os.write(descriptor, remaining)
                require(count > 0,
                        "complete actual public evidence was truncated")
                remaining = remaining[count:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def run_self_oracle(options: argparse.Namespace) -> dict[str, Any]:
    provenance = authenticate_reference_prerequisites(
        options.source_sha256, options.protocol_sha256,
    )
    locales = _locale_names(options)
    _preflight_destinations((SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE))
    completed: dict[str, dict[str, Any]] = {}
    processes: dict[str, dict[str, Any]] = {}
    try:
        for role in ("reference_a", "reference_b"):
            report, process = _run_reference_worker(
                role, options.source_sha256, options.protocol_sha256, locales,
            )
            completed[role] = report
            processes[role] = process
        first = completed["reference_a"]
        second = completed["reference_b"]
        require(first["records"] == second["records"]
                and first["record_sha256"] == second["record_sha256"],
                "the complete two independently started Python references differ")
        result = {
            "schema": SCHEMA + "-self-oracle",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "v17_source_path": V17_SOURCE_RELATIVE,
            "v17_source_sha256": V17_SOURCE_SHA256,
            "v17_protocol_path": V17_PROTOCOL_RELATIVE,
            "v17_protocol_sha256": V17_PROTOCOL_SHA256,
            "v18_source_path": V18_SOURCE_RELATIVE,
            "v18_source_sha256": V18_SOURCE_SHA256,
            "v18_protocol_path": V18_PROTOCOL_RELATIVE,
            "v18_protocol_sha256": V18_PROTOCOL_SHA256,
            "historical_v18_failure_path": V18_HISTORICAL_FAILURE_RELATIVE,
            "historical_v18_failure_sha256": V18_HISTORICAL_FAILURE_SHA256,
            "historical_failure_qualifies_current_build": False,
            "v5_reference_path": v17.V5_REFERENCE_RELATIVE,
            "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
            "original_public_methods": 152,
            "original_applicable_passes": 151,
            "original_named_private_debug_skips": 1,
            "original_public_method_waivers": 0,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cohorts": EXPECTED_COHORTS,
            "cases": EXPECTED_CASES,
            "actual_independent_reference_count": 2,
            "retained_additional_cases_per_worker": EXPECTED_ADDITIONAL_CASES,
            "returned_additional_cases_per_worker":
                first["returned_additional_cases"],
            "raised_additional_cases_per_worker":
                first["raised_additional_cases"],
            "successful_real_locale_cases_per_worker": EXPECTED_LOCALE_CASES,
            "real_locale_transitions_per_worker": EXPECTED_LOCALE_TRANSITIONS,
            "reference_worker_reports": completed,
            "reference_worker_processes": processes,
            "record_sha256": first["record_sha256"],
            "candidate_audits_read": provenance["candidate_audits_read"],
            "candidate_proofs_read": provenance["candidate_proofs_read"],
            "candidate_imports": provenance["candidate_imports"],
            "v12_sources_read": provenance["v12_sources_read"],
            "current_graph_candidate_qualification":
                CURRENT_GRAPH_CANDIDATE_QUALIFICATION,
            "candidate_evidence_current": CURRENT_GRAPH_CANDIDATE_EVIDENCE,
            "current_graph_candidate_qualification_reason":
                CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
            "subinterpreter_coverage": "NOT RUN",
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        exclusive_write(result, SELF_ORACLE_RELATIVE)
        return result
    except BaseException as error:
        failed: dict[str, Any] = {
            "schema": SCHEMA + "-self-oracle-failure",
            "status": "FAIL",
            "synthetic": False,
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "completed_reference_workers": completed,
            "completed_reference_worker_processes": processes,
            **_error_details(error),
            "candidate_audits_read": 0,
            "candidate_proofs_read": 0,
            "candidate_imports": 0,
            "v12_sources_read": 0,
            "current_graph_candidate_qualification":
                CURRENT_GRAPH_CANDIDATE_QUALIFICATION,
            "candidate_evidence_current": CURRENT_GRAPH_CANDIDATE_EVIDENCE,
            "current_graph_candidate_qualification_reason":
                CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        if isinstance(error, PublicSurfaceV19WorkerFailure):
            failed["failed_role"] = error.role
            failed["actual_failure_details"] = error.details
        exclusive_write(failed, SELF_ORACLE_FAILURE_RELATIVE)
        raise


def authenticate_surface_reference(
    provenance: Mapping[str, Any],
    *,
    source_sha256: str,
    protocol_sha256: str,
    reference_sha256: str | None,
) -> dict[str, Any]:
    require(
        provenance.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and provenance.get("candidate_imports") == 0
        and provenance.get("candidate_audits_read") == 0
        and provenance.get("candidate_proofs_read") == 0
        and provenance.get("v12_sources_read") == 0,
        "authenticate the candidate-free original baseline before proof access",
    )
    require(valid_sha256(reference_sha256),
            "BLOCKED: independently publish the actual complete two-worker "
            "V19 Python reference before any candidate audit or proof")
    raw = read_frozen(SELF_ORACLE_RELATIVE, str(reference_sha256), MAX_REPORT_BYTES)
    result = strict_canonical(raw, SELF_ORACLE_RELATIVE)
    require(
        result.get("schema") == SCHEMA + "-self-oracle"
        and result.get("status") == "PASS"
        and result.get("synthetic") is False
        and result.get("python") == "3.14.6"
        and result.get("source_path") == SOURCE_RELATIVE
        and result.get("source_sha256") == source_sha256
        and result.get("protocol_path") == PROTOCOL_RELATIVE
        and result.get("protocol_sha256") == protocol_sha256
        and result.get("v17_source_sha256") == V17_SOURCE_SHA256
        and result.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and result.get("v18_source_sha256") == V18_SOURCE_SHA256
        and result.get("v18_protocol_sha256") == V18_PROTOCOL_SHA256
        and result.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and result.get("historical_v18_failure_path")
        == V18_HISTORICAL_FAILURE_RELATIVE
        and result.get("historical_v18_failure_sha256")
        == V18_HISTORICAL_FAILURE_SHA256
        and result.get("historical_failure_qualifies_current_build") is False
        and result.get("original_public_methods") == 152
        and result.get("original_applicable_passes") == 151
        and result.get("original_named_private_debug_skips") == 1
        and result.get("original_public_method_waivers") == 0
        and result.get("matrix_sha256") == MATRIX_SHA256
        and result.get("stimulus_sha256") == STIMULUS_SHA256
        and result.get("cohorts") == EXPECTED_COHORTS
        and result.get("cases") == EXPECTED_CASES
        and result.get("actual_independent_reference_count") == 2
        and result.get("retained_additional_cases_per_worker")
        == EXPECTED_ADDITIONAL_CASES
        and type(result.get("returned_additional_cases_per_worker")) is int
        and type(result.get("raised_additional_cases_per_worker")) is int
        and result["returned_additional_cases_per_worker"]
        + result["raised_additional_cases_per_worker"]
        == EXPECTED_ADDITIONAL_CASES
        and result.get("successful_real_locale_cases_per_worker")
        == EXPECTED_LOCALE_CASES
        and result.get("real_locale_transitions_per_worker")
        == EXPECTED_LOCALE_TRANSITIONS
        and result.get("candidate_audits_read") == 0
        and result.get("candidate_proofs_read") == 0
        and result.get("candidate_imports") == 0
        and result.get("v12_sources_read") == 0
        and result.get("current_graph_candidate_qualification")
        == CURRENT_GRAPH_CANDIDATE_QUALIFICATION
        and result.get("candidate_evidence_current")
        == CURRENT_GRAPH_CANDIDATE_EVIDENCE
        and result.get("current_graph_candidate_qualification_reason")
        == CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON
        and result.get("subinterpreter_coverage") == "NOT RUN"
        and result.get("holdout_cases_read") == 0
        and result.get("performance_fixtures_read") == 0
        and result.get("benchmark_or_timing_executed") is False
        and result.get("performance") == "NOT MEASURED",
        "the exact actual independently published V19 Python reference failed",
    )
    workers = result.get("reference_worker_reports")
    processes = result.get("reference_worker_processes")
    require(isinstance(workers, dict)
            and set(workers) == {"reference_a", "reference_b"}
            and isinstance(processes, dict)
            and set(processes) == {"reference_a", "reference_b"},
            "both independently isolated complete Python workers are mandatory")
    first = validate_reference_worker(
        workers["reference_a"], role="reference_a",
        source_sha256=source_sha256, protocol_sha256=protocol_sha256,
    )
    second = validate_reference_worker(
        workers["reference_b"], role="reference_b",
        source_sha256=source_sha256, protocol_sha256=protocol_sha256,
    )
    validate_process_streams(processes["reference_a"], role="reference_a",
                             expected_document=first)
    validate_process_streams(processes["reference_b"], role="reference_b",
                             expected_document=second)
    require(first["records"] == second["records"]
            and first["record_sha256"] == second["record_sha256"]
            and first["record_sha256"] == result.get("record_sha256")
            and first["returned_additional_cases"]
            == result["returned_additional_cases_per_worker"]
            and first["raised_additional_cases"]
            == result["raised_additional_cases_per_worker"],
            "the two complete Python streams or their expected errors disagree")
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "reference_sha256": str(reference_sha256),
        "baseline_records": first["records"],
        "record_sha256": first["record_sha256"],
        "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
    }


def import_frozen_validator(name: str, relative: str, fingerprint: str) -> Any:
    read_frozen(relative, fingerprint, MAX_SOURCE_BYTES)
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "a candidate imported before an authenticated frozen owner")
    module = importlib.import_module(name)
    require(os.path.abspath(module.__file__) == str(ROOT / relative),
            "the exact source-authenticated frozen validator was substituted")
    read_frozen(relative, fingerprint, MAX_SOURCE_BYTES)
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "an ownership validator imported a native candidate too early")
    return module


def decode_producer_canonical(
    payload: bytes,
    label: str,
    producer: Any,
) -> dict[str, Any]:
    """Preserve the producing V11/V12 pretty canonical bytes exactly."""
    require(type(payload) is bytes and 0 < len(payload) <= MAX_REPORT_BYTES,
            "an original producer document must retain its complete bytes")
    decoder = getattr(producer, "decode_json", None)
    encoder = getattr(producer, "canonical", None)
    require(callable(decoder) and callable(encoder),
            "the immutable producing proof codec was replaced")
    result = decoder(payload, label)
    require(isinstance(result, dict)
            and encoder(result) == payload,
            "the immutable complete producer-canonical proof changed: " + label)
    return result


def validate_audited_graph_identity(
    graph: Any,
    snapshots: Any,
    specifications: Any,
) -> dict[str, Any]:
    """Bind all 12 owned source hashes and all five native hashes to V10."""
    require(
        isinstance(graph, dict)
        and graph.get("all_family_audit_qualified") is True
        and isinstance(graph.get("all_family_source_sha256_by_path"), dict)
        and isinstance(graph.get("all_family_native_elf_sha256_by_path"), dict)
        and len(graph["all_family_source_sha256_by_path"]) == 12
        and len(graph["all_family_native_elf_sha256_by_path"]) == 5
        and isinstance(snapshots, Mapping)
        and set(snapshots) == set(FAMILIES)
        and isinstance(specifications, Mapping)
        and set(specifications) == set(FAMILIES),
        "the real V10 audited all-family 12-source/five-native graph is missing",
    )
    audited_sources = graph["all_family_source_sha256_by_path"]
    audited_native = graph["all_family_native_elf_sha256_by_path"]
    require(all(type(path) is str and valid_sha256(value)
                for path, value in audited_sources.items())
            and all(type(path) is str and valid_sha256(value)
                    for path, value in audited_native.items()),
            "the complete real audited owner graph has an invalid fingerprint")
    all_source_paths: set[str] = set()
    all_native_paths: set[str] = set()
    for family in FAMILIES:
        snapshot = snapshots[family]
        detail = specifications[family]
        require(isinstance(snapshot, Mapping)
                and isinstance(detail, Mapping)
                and snapshot.get("family") == family
                and snapshot.get("module")
                == "candidates." + family + "_candidate"
                and isinstance(detail.get("sources"), (tuple, list))
                and isinstance(detail.get("native"), Mapping)
                and isinstance(snapshot.get("source_sha256_by_path"), Mapping)
                and isinstance(snapshot.get("native_sha256_by_path"), Mapping),
                "a genuine audited family source/native graph was substituted: "
                + family)
        expected_sources = set(detail["sources"])
        expected_native = set(detail["native"].values())
        require(len(expected_sources) == len(detail["sources"])
                and len(expected_native) == len(detail["native"])
                and not (expected_sources & all_source_paths)
                and not (expected_native & all_native_paths)
                and set(snapshot["source_sha256_by_path"]) == expected_sources
                and set(snapshot["native_sha256_by_path"]) == expected_native
                and expected_sources <= set(audited_sources)
                and expected_native <= set(audited_native)
                and dict(snapshot["source_sha256_by_path"]) == {
                    path: audited_sources[path] for path in expected_sources
                }
                and dict(snapshot["native_sha256_by_path"]) == {
                    path: audited_native[path] for path in expected_native
                },
                "a real owned source or native binary changed after both "
                "passing V10 audits: " + family)
        all_source_paths.update(expected_sources)
        all_native_paths.update(expected_native)
    require(all_source_paths == set(audited_sources)
            and all_native_paths == set(audited_native),
            "the actual V10 audit omitted or added an owned source or native ELF")
    return graph


def _restore_durable_producer(
    producer: Any,
    wrapper: Mapping[str, Any],
    *,
    label: str,
) -> subprocess.CompletedProcess[bytes]:
    code = wrapper.get("original_worker_returncode")
    require(type(code) is int and code == 0,
            "the actual qualified original " + label + " worker did not pass")
    return subprocess.CompletedProcess(
        args=["durably-recorded-genuine-original-" + label],
        returncode=code,
        stdout=producer.restore_complete_stream(
            wrapper.get("original_worker_stdout"),
            "complete actual original " + label + " worker stdout",
        ),
        stderr=producer.restore_complete_stream(
            wrapper.get("original_worker_stderr"),
            "complete actual original " + label + " worker stderr",
        ),
    )


def _authenticate_v11_family(
    family: str,
    pins: Mapping[str, str],
    *,
    owner: Any,
    strict: Any,
    v11: Any,
    v8: Any,
    contract: Any,
    audits: Mapping[str, Any],
    history: Mapping[str, Any],
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    require(v11.snapshot_family(family) == snapshot,
            "the real audited owned candidate changed before full V11 proof "
            "validation: " + family)
    state = {
        "owner": owner,
        "strict": strict,
        "v8": v8,
        "history": history,
        "snapshot": snapshot,
        "audits": audits,
    }
    edge_archive_relative = V11_EDGE_ARCHIVE_RELATIVES[family]
    edge_proof_relative = V11_EDGE_PROOF_RELATIVES[family]
    edge_archive = read_frozen(
        edge_archive_relative,
        pins[family + "_edge_archive"],
        MAX_ARCHIVE_BYTES,
    )
    edge_proof_raw = read_frozen(
        edge_proof_relative,
        pins[family + "_edge_proof"],
        MAX_ARCHIVE_BYTES,
    )
    edge_path = ROOT / edge_archive_relative
    edge_proof_path = ROOT / edge_proof_relative
    require(edge_path == v11.edge_target(family, True, True)
            and edge_proof_path == v11.edge_proof_target(family, True, True),
            "the genuine exact-family qualified V11 edge pair was substituted")
    edge_original, edge_result, passed = v8.validate_original_edge(
        edge_archive, edge_path, family, snapshot, contract,
    )
    require(isinstance(edge_original, dict)
            and isinstance(edge_result, dict)
            and passed is True
            and edge_result.get("failed") == 0
            and edge_result.get("checks") == v11.EDGE_CHECKS
            and edge_result.get("category_count") == v11.EDGE_CATEGORIES,
            "the original complete 223,198-case qualified edge failed: " + family)
    edge_wrapper = decode_producer_canonical(
        edge_proof_raw, edge_proof_relative, v11,
    )
    v18.validate_durable_pair_identity(
        edge_wrapper,
        family,
        deep=False,
        archive_relative=edge_archive_relative,
        archive_sha256=pins[family + "_edge_archive"],
        proof_relative=edge_proof_relative,
        snapshot=snapshot,
        v10_base_report_sha256=pins["v10_base_report"],
        v10_strict_report_sha256=pins["v10_strict_report"],
    )
    edge_producer = _restore_durable_producer(
        v11, edge_wrapper, label="v11-edge-" + family,
    )
    v11.validate_durable_wrapper(
        edge_wrapper,
        family,
        state,
        qualified=True,
        deep=False,
        passed=True,
        original=edge_original,
        archive_path=edge_path,
        archive_sha256=pins[family + "_edge_archive"],
        archive_bytes=len(edge_archive),
        owner_before=edge_wrapper.get("corrected_v10_native_owner_before"),
        owner_after=edge_wrapper.get("corrected_v10_native_owner_after"),
        producer=edge_producer,
    )
    qualified_edge = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": edge_archive_relative,
        "archive_sha256": pins[family + "_edge_archive"],
        "proof_path": edge_proof_relative,
        "proof_sha256": pins[family + "_edge_proof"],
    }

    deep_archive_relative = V11_DEEP_ARCHIVE_RELATIVES[family]
    deep_proof_relative = V11_DEEP_PROOF_RELATIVES[family]
    deep_archive = read_frozen(
        deep_archive_relative,
        pins[family + "_deep_archive"],
        MAX_ARCHIVE_BYTES,
    )
    deep_proof_raw = read_frozen(
        deep_proof_relative,
        pins[family + "_deep_proof"],
        MAX_ARCHIVE_BYTES,
    )
    deep_path = ROOT / deep_archive_relative
    deep_proof_path = ROOT / deep_proof_relative
    require(deep_path == v11.deep_target(family, True)
            and deep_proof_path == v11.deep_proof_target(family, True),
            "the genuine exact-family qualified V11 deep pair was substituted")
    deep_original, deep_passed = v8.validate_deep(
        deep_archive, family, edge_result, snapshot, contract,
    )
    require(isinstance(deep_original, dict)
            and deep_passed is True
            and deep_original.get("public_mismatch_count") == 0,
            "the genuine complete 393-check original deep contract failed: "
            + family)
    deep_wrapper = decode_producer_canonical(
        deep_proof_raw, deep_proof_relative, v11,
    )
    v18.validate_durable_pair_identity(
        deep_wrapper,
        family,
        deep=True,
        archive_relative=deep_archive_relative,
        archive_sha256=pins[family + "_deep_archive"],
        proof_relative=deep_proof_relative,
        snapshot=snapshot,
        v10_base_report_sha256=pins["v10_base_report"],
        v10_strict_report_sha256=pins["v10_strict_report"],
        qualified_edge=qualified_edge,
    )
    deep_producer = _restore_durable_producer(
        v11, deep_wrapper, label="v11-deep-" + family,
    )
    v11.validate_durable_wrapper(
        deep_wrapper,
        family,
        state,
        qualified=True,
        deep=True,
        passed=True,
        original=deep_original,
        archive_path=deep_path,
        archive_sha256=pins[family + "_deep_archive"],
        archive_bytes=len(deep_archive),
        owner_before=deep_wrapper.get("corrected_v10_native_owner_before"),
        owner_after=deep_wrapper.get("corrected_v10_native_owner_after"),
        producer=deep_producer,
        qualified_edge=qualified_edge,
    )
    require(edge_wrapper.get("preserved_immutable_history") == history
            and deep_wrapper.get("preserved_immutable_history") == history
            and v11.snapshot_family(family) == snapshot,
            "a complete real V11 proof changed the independently authenticated "
            "history, owned source, or native binary: " + family)
    return {
        "family": family,
        "snapshot": dict(snapshot),
        "edge": qualified_edge,
        "deep": {
            "status": "PASS",
            "campaign_qualified": True,
            "archive_path": deep_archive_relative,
            "archive_sha256": pins[family + "_deep_archive"],
            "proof_path": deep_proof_relative,
            "proof_sha256": pins[family + "_deep_proof"],
        },
        "validated_edge_original": edge_original,
        "validated_edge_result": edge_result,
        "validated_edge_archive_bytes": edge_archive,
        "validated_edge_wrapper": edge_wrapper,
        "validated_edge_wrapper_bytes": edge_proof_raw,
        "validated_deep_original": deep_original,
        "validated_deep_archive_bytes": deep_archive,
        "validated_deep_wrapper": deep_wrapper,
        "validated_deep_wrapper_bytes": deep_proof_raw,
    }


def v12_retry_pin_values(values: Mapping[str, Any]) -> dict[str, str]:
    expected = {family + "_deep_retry_proof" for family in FAMILIES}
    require(
        isinstance(values, Mapping)
        and set(values) == expected
        and all(valid_sha256(values.get(name)) for name in expected)
        and len({values[name] for name in expected}) == len(expected),
        "BLOCKED: publish all three distinct actual qualified V12 deep-retry "
        "owner-proof SHA-256 values before importing any candidate",
    )
    return {name: str(values[name]) for name in sorted(expected)}


def authenticate_v12_retry_proofs(
    durable: Mapping[str, Any],
    supplied: Mapping[str, Any],
) -> dict[str, Any]:
    """Fail closed until all three actual published V12 retries authenticate."""
    require(isinstance(durable, Mapping)
            and isinstance(durable.get("families"), dict)
            and set(durable["families"]) == set(FAMILIES)
            and isinstance(durable.get("pins"), dict)
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "validate all 12 real V11 artifacts before opening V12 retry proofs")
    pins = v12_retry_pin_values(supplied)
    read_frozen(V12_PROTOCOL_RELATIVE, V12_PROTOCOL_SHA256, MAX_SOURCE_BYTES)
    v12 = import_frozen_validator(
        "tools.postfinal_current_build_proofs_v12",
        V12_SOURCE_RELATIVE,
        V12_SOURCE_SHA256,
    )
    v11 = durable.get("v11")
    v8 = durable.get("v8")
    owner = durable.get("owner")
    audits = durable.get("audits")
    history = durable.get("history")
    contract = durable.get("contract")
    require(getattr(v12, "SCHEMA", None)
            == "rebar-postfinal-current-build-proofs-v12"
            and getattr(v12, "SOURCE_RELATIVE", None) == V12_SOURCE_RELATIVE
            and getattr(v12, "PROTOCOL_RELATIVE", None)
            == V12_PROTOCOL_RELATIVE
            and getattr(v12, "PROTOCOL_SHA256", None) == V12_PROTOCOL_SHA256
            and getattr(v12, "V11_SOURCE_SHA256", None)
            == v18.V11_SOURCE_SHA256
            and getattr(v12, "V11_PROTOCOL_SHA256", None)
            == v18.V11_PROTOCOL_SHA256
            and getattr(v12, "ACTUAL_V10_BASE_REPORT_SHA256", None)
            == durable["pins"]["v10_base_report"]
            and getattr(v12, "ACTUAL_V10_STRICT_REPORT_SHA256", None)
            == durable["pins"]["v10_strict_report"]
            and getattr(v12, "v11", None) is v11
            and isinstance(audits, Mapping)
            and isinstance(history, Mapping),
            "the immutable finally published V12 retry producer was substituted")
    validator = getattr(v12, "validate_retry_proof", None)
    require(callable(validator)
            and callable(getattr(v12, "authenticate_prior_incident", None))
            and callable(getattr(v12, "authenticate_controller", None))
            and callable(getattr(v12, "validate_parent_environment", None)),
            "BLOCKED: an exact independently frozen V12 retry validator is "
            "required before importing any candidate")
    controller = v12.authenticate_controller()
    require(controller == {
        "source_path": V12_SOURCE_RELATIVE,
        "source_sha256": V12_SOURCE_SHA256,
        "protocol_path": V12_PROTOCOL_RELATIVE,
        "protocol_sha256": V12_PROTOCOL_SHA256,
        "v11_format_source_path": v18.V11_SOURCE_RELATIVE,
        "v11_format_source_sha256": v18.V11_SOURCE_SHA256,
        "v11_format_protocol_path": v18.V11_PROTOCOL_RELATIVE,
        "v11_format_protocol_sha256": v18.V11_PROTOCOL_SHA256,
    }, "the complete actual immutable V12/V11 controller identity changed")
    incident, prior_original, prior_original_raw = (
        v12.authenticate_prior_incident({
            "owner": owner,
            "v8": v8,
            "audits": audits,
        })
    )
    rust = durable["families"]["rust"]
    independent_prior, prior_passed = v8.validate_deep(
        prior_original_raw,
        "rust",
        rust["validated_edge_result"],
        rust["snapshot"],
        contract,
    )
    require(prior_passed is True
            and independent_prior == prior_original
            and independent_prior.get("public_mismatch_count") == 0
            and isinstance(incident, dict)
            and incident.get("actual_v11_first_invocation_status") == "FAIL"
            and incident.get("first_failure_retroactively_qualified") is False,
            "the two authentic first V11 failure archives or actual invalidated "
            "393-check Rust original were substituted")
    complete: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        relative = V12_DEEP_RETRY_PROOF_RELATIVES[family]
        fingerprint = pins[family + "_deep_retry_proof"]
        raw = read_frozen(relative, fingerprint, MAX_ARCHIVE_BYTES)
        document = decode_producer_canonical(raw, relative, v11)
        family_state = durable["families"][family]
        require(
            document.get("schema") == V12_RETRY_SCHEMA
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("mode") == "qualified-deep"
            and document.get("campaign_qualified") is True
            and document.get("candidate_family") == CONTRACT_NAMES[family]
            and document.get("candidate_module")
            == "candidates." + family + "_candidate"
            and document.get("retry_proof_path") == relative
            and document.get("actual_invoking_controller") == "V12"
            and document.get("actual_invoking_controller_path")
            == V12_SOURCE_RELATIVE
            and document.get("actual_invoking_controller_sha256")
            == V12_SOURCE_SHA256
            and document.get("actual_retry_protocol_path")
            == V12_PROTOCOL_RELATIVE
            and document.get("actual_retry_protocol_sha256")
            == V12_PROTOCOL_SHA256
            and document.get("v11_executed_this_retry") is False
            and document.get("original_v11_format_archive_path")
            == V11_DEEP_ARCHIVE_RELATIVES[family]
            and document.get("original_v11_format_archive_sha256")
            == durable["pins"][family + "_deep_archive"]
            and document.get("original_v11_format_owner_proof_path")
            == V11_DEEP_PROOF_RELATIVES[family]
            and document.get("original_v11_format_owner_proof_sha256")
            == durable["pins"][family + "_deep_proof"]
            and document.get("qualified_original_v11_edge")
            == family_state["edge"]
            and document.get("full_current_family_source_sha256")
            == family_state["snapshot"]["source_sha256_by_path"]
            and document.get("full_current_family_native_elf_sha256")
            == family_state["snapshot"]["native_sha256_by_path"]
            and type(document.get("actual_original_worker_returncode")) is int
            and document["actual_original_worker_returncode"] == 0
            and document.get("performance") == "NOT MEASURED"
            and document.get("holdout") == "NOT ACCESSED",
            "a complete exact-family qualified V12 retry proof was forged",
        )
        command = document.get("actual_original_worker_command")
        require(isinstance(command, list)
                and len(command) == 10
                and all(type(item) is str for item in command)
                and command[:8] == [
                    str(v17.PINNED_PYTHON), "-I", "-B", "-c",
                    v11.DEEP_LAUNCHER, str(ROOT),
                    "candidates." + family + "_candidate",
                    str(ROOT / V11_EDGE_ARCHIVE_RELATIVES[family]),
                ],
                "the actual frozen V12 original deep-worker command changed: "
                + family)
        temporary = Path(command[8])
        private = Path(command[9])
        require(temporary.is_absolute()
                and private.is_absolute()
                and temporary.parent == private
                and private.parent == Path("/tmp").resolve()
                and private.name.startswith(
                    "rebar-v12-original-deep-" + family + "-",
                )
                and temporary.name == (
                    "RUST-V8-DEEP-CONTRACT-" + CONTRACT_NAMES[family]
                    + "-POSTFINAL-CURRENT-BUILD-V12-PRIVATE.json.gz"
                ),
                "the actual V12 original worker escaped its genuine private "
                "family-specific temporary directory")
        original_stdout = v11.restore_complete_stream(
            document.get("actual_original_worker_stdout"),
            "complete actual separately recorded V12 retry worker stdout",
        )
        original_stderr = v11.restore_complete_stream(
            document.get("actual_original_worker_stderr"),
            "complete actual separately recorded V12 retry worker stderr",
        )
        original_process = subprocess.CompletedProcess(
            args=command,
            returncode=document["actual_original_worker_returncode"],
            stdout=original_stdout,
            stderr=original_stderr,
        )
        v12.validate_original_process(original_process, command)
        parent = v12.validate_parent_environment(
            document.get("actual_verified_parent_environment"),
        )
        state = {
            "owner": owner,
            "strict": durable["strict"],
            "v8": v8,
            "history": history,
            "snapshot": family_state["snapshot"],
            "audits": audits,
            "parent_environment": parent,
            "controller": controller,
            "prior_incident": incident,
            "prior_invalidated_original": prior_original,
            "prior_invalidated_original_raw": prior_original_raw,
        }
        owner_before = document.get("corrected_v10_native_owner_before")
        owner_after = document.get("corrected_v10_native_owner_after")
        deep_wrapper = family_state["validated_deep_wrapper"]
        require(owner_before
                == deep_wrapper.get("corrected_v10_native_owner_before")
                and owner_after
                == deep_wrapper.get("corrected_v10_native_owner_after")
                and document.get("actual_original_worker_stdout")
                == deep_wrapper.get("original_worker_stdout")
                and document.get("actual_original_worker_stderr")
                == deep_wrapper.get("original_worker_stderr")
                and document.get("actual_original_worker_returncode")
                == deep_wrapper.get("original_worker_returncode")
                and v11.snapshot_family(family) == family_state["snapshot"],
                "the real V12 retry does not belong to its authentic complete "
                "V11 deep archive, producer, and before/after owners")
        # Rebuild and validate every field with the exact immutable V12
        # producer; never infer history or original observations from its proof.
        validated = validator(
            document,
            family,
            state,
            original=family_state["validated_deep_original"],
            original_raw=family_state["validated_deep_archive_bytes"],
            wrapper=deep_wrapper,
            wrapper_raw=family_state["validated_deep_wrapper_bytes"],
            owner_before=owner_before,
            owner_after=owner_after,
            producer=original_process,
            command=command,
            qualified_edge=family_state["edge"],
        )
        require(validated is document,
                "the actual complete frozen V12 retry owner proof failed")
        complete[family] = {
            "status": "PASS",
            "proof_path": relative,
            "proof_sha256": fingerprint,
            "source_sha256": V12_SOURCE_SHA256,
            "protocol_sha256": V12_PROTOCOL_SHA256,
            "full_v11_archive_and_owner_proof_validated": True,
        }
    require(set(complete) == set(FAMILIES)
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "all three actual V12 retry proofs must pass before candidate import")
    return {"module": v12, "pins": pins, "families": complete}


def authenticate_durable_candidate_prerequisites(
    surface_reference: Mapping[str, Any],
    supplied: Mapping[str, Any],
    retry_pins: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        surface_reference.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and valid_sha256(surface_reference.get("reference_sha256"))
        and valid_sha256(surface_reference.get("record_sha256"))
        and isinstance(surface_reference.get("baseline_records"), list)
        and len(surface_reference["baseline_records"]) == EXPECTED_CASES
        and not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
        "authenticate both complete Python references before any native proof",
    )
    pins = v18.proof_pin_values(supplied)
    read_frozen(
        v18.V10_OWNERSHIP_PROTOCOL_RELATIVE,
        v18.V10_OWNERSHIP_PROTOCOL_SHA256,
        MAX_SOURCE_BYTES,
    )
    read_frozen(
        v18.V11_PROTOCOL_RELATIVE,
        v18.V11_PROTOCOL_SHA256,
        MAX_SOURCE_BYTES,
    )
    owner = import_frozen_validator(
        "tools.postfinal_from_scratch_audit_v10",
        v18.V10_OWNER_RELATIVE,
        v18.V10_OWNER_SHA256,
    )
    strict = import_frozen_validator(
        "tools.postfinal_no_delegation_audit_v10",
        v18.V10_STRICT_RELATIVE,
        v18.V10_STRICT_SHA256,
    )
    v11 = import_frozen_validator(
        "tools.postfinal_current_build_proofs_v11",
        v18.V11_SOURCE_RELATIVE,
        v18.V11_SOURCE_SHA256,
    )
    require(strict.independent is owner
            and v11.SCHEMA == "rebar-postfinal-current-build-proofs-v11"
            and v11.REFRESH_PROTOCOL_SHA256 == v18.V11_PROTOCOL_SHA256
            and v11.V10_BASE_SOURCE_SHA256 == v18.V10_OWNER_SHA256
            and v11.V10_STRICT_SOURCE_SHA256 == v18.V10_STRICT_SHA256
            and v11.V10_OWNERSHIP_PROTOCOL_SHA256
            == v18.V10_OWNERSHIP_PROTOCOL_SHA256
            and v11.BASELINE_SHA256 == v17.V5_REFERENCE_SHA256
            and tuple(v11.FAMILIES) == FAMILIES,
            "an immutable complete all-family V10/V11 native owner was replaced")
    audit_pins = v11.validated_report_pins(
        True, pins["v10_base_report"], pins["v10_strict_report"],
    )
    require(isinstance(audit_pins, dict)
            and audit_pins.get("base_source") == v18.V10_OWNER_SHA256
            and audit_pins.get("strict_source") == v18.V10_STRICT_SHA256,
            "the exact independent V10 report or validator fingerprint changed")
    audits = v11.audit_v11_reports(owner, strict, audit_pins)
    require(isinstance(audits, dict)
            and isinstance(audits.get("graph"), dict)
            and audits["graph"].get("source_count") == 12
            and audits["graph"].get("native_binary_count") == 5,
            "both actual complete three-family V10 native-owner audits failed")
    v8 = v11.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        v11.V8_PROOF_RELATIVE,
        v11.V8_PROOF_SHA256,
    )
    contract = v8.load_contract()
    history = v11.authenticate_history(v8, owner)
    require(isinstance(history, Mapping),
            "the genuine immutable V10/V11 first-failure history was replaced")
    snapshots = {
        family: v11.snapshot_family(family)
        for family in FAMILIES
    }
    graph = validate_audited_graph_identity(
        v11.audited_graph_provenance({"audits": audits}),
        snapshots,
        v11.FAMILIES,
    )
    complete = {
        family: _authenticate_v11_family(
            family,
            pins,
            owner=owner,
            strict=strict,
            v11=v11,
            v8=v8,
            contract=contract,
            audits=audits,
            history=history,
            snapshot=snapshots[family],
        )
        for family in FAMILIES
    }
    require(set(complete) == set(FAMILIES)
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "all 12 genuine independently owned V11 artifacts must pass "
            "before opening V12 retry proofs")
    durable: dict[str, Any] = {
        "owner": owner,
        "strict": strict,
        "v11": v11,
        "v8": v8,
        "contract": contract,
        "history": history,
        "audits": audits,
        "audited_graph": graph,
        "families": complete,
        "pins": pins,
    }
    durable["v12_retry"] = authenticate_v12_retry_proofs(durable, retry_pins)
    return durable


def _candidate_configuration(
    family: str,
    *,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
    expected_native: Mapping[str, str],
) -> dict[str, Any]:
    return verify_embedded_configuration({
        "schema": SCHEMA + "-embedded-configuration",
        "family": family,
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v18_source_sha256": V18_SOURCE_SHA256,
        "v18_protocol_sha256": V18_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "iso8859_1_locale": locales["iso8859_1"],
        "utf8_locale": locales["utf8"],
        "expected_native_sha256": dict(expected_native),
    })


def _decode_guarded_stderr(stderr: bytes, family: str) -> dict[str, Any] | None:
    if not stderr:
        return None
    first = stderr.split(b"\n", 1)[0]
    try:
        result = strict_canonical(first, family + " complete guarded failure")
    except (
        PublicSurfaceV19Error, v17.PublicSurfaceError,
        ValueError, TypeError, UnicodeError,
    ):
        return None
    require(result.get("schema") == SCHEMA + "-embedded-public-failure"
            and result.get("status") == "FAIL"
            and result.get("family") == family,
            "the actual same-process guarded candidate failure was substituted")
    return result


def _first_actual_public_mismatch(
    actual: Any,
    expected: Any,
) -> dict[str, Any] | None:
    """Preserve the first actually observed difference without inventing rows."""
    if not isinstance(actual, list) or not isinstance(expected, list):
        return None
    for index, (actual_row, expected_row) in enumerate(
        zip(actual, expected, strict=False),
    ):
        if actual_row != expected_row:
            case_id = (
                actual_row.get("id")
                if isinstance(actual_row, Mapping)
                else expected_row.get("id")
                if isinstance(expected_row, Mapping)
                else None
            )
            return {
                "index": index,
                "case_id": case_id,
                "actual_record": actual_row,
                "expected_record": expected_row,
            }
    if len(actual) == len(expected):
        return None
    index = min(len(actual), len(expected))
    actual_row = actual[index] if index < len(actual) else None
    expected_row = expected[index] if index < len(expected) else None
    case_id = (
        actual_row.get("id")
        if isinstance(actual_row, Mapping)
        else expected_row.get("id")
        if isinstance(expected_row, Mapping)
        else None
    )
    return {
        "index": index,
        "case_id": case_id,
        "actual_record": actual_row,
        "expected_record": expected_row,
    }


def _zero_exit_guarded_failure_details(
    family: str,
    error: BaseException,
    *,
    process: Mapping[str, Any],
    owner_before: Mapping[str, Any],
    composed_worker_sha256: str,
    failure_stage: str,
    baseline: list[dict[str, Any]],
    actual_owner_report: Mapping[str, Any] | None,
    actual_public_observations: Mapping[str, Any] | None,
    actual_snapshot: Mapping[str, Any] | None,
    actual_owner_after: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Retain complete original zero-exit child evidence at every stage."""
    require(
        isinstance(process, Mapping)
        and process.get("role") == family
        and type(process.get("returncode")) is int
        and process.get("returncode") == 0
        and isinstance(owner_before, Mapping)
        and valid_sha256(composed_worker_sha256),
        "a failed zero-exit native owner lost its genuine role or provenance",
    )
    restore_complete_stream(
        process.get("stdout"),
        label=family + " complete failed zero-exit candidate stdout",
    )
    restore_complete_stream(
        process.get("stderr"),
        label=family + " complete failed zero-exit candidate stderr",
    )
    details: dict[str, Any] = {
        "role": family,
        "returncode": 0,
        "stdout": process["stdout"],
        "stderr": process["stderr"],
        "complete_original_worker_streams": dict(process),
        "owner_before": dict(owner_before),
        "composed_worker_sha256": composed_worker_sha256,
        "failure_stage": failure_stage,
        **_error_details(error),
    }
    if actual_owner_report is not None:
        details["actual_decoded_owner_report"] = actual_owner_report
    if actual_public_observations is not None:
        details["actual_embedded_public_observations"] = (
            actual_public_observations
        )
        records = actual_public_observations.get("records")
        if isinstance(records, list):
            details["completed_records"] = records
            details["completed_count"] = len(records)
            mismatch = _first_actual_public_mismatch(records, baseline)
            if mismatch is not None:
                details["first_actual_public_mismatch"] = mismatch
    if actual_snapshot is not None:
        details["actual_observed_family_snapshot"] = actual_snapshot
    if actual_owner_after is not None:
        details["actual_observed_owner_after"] = actual_owner_after
    return details


def validate_zero_exit_guarded_worker(
    family: str,
    *,
    retained_process: Mapping[str, Any],
    owner_before: Mapping[str, Any],
    composed_worker_sha256: str,
    expected_snapshot: Mapping[str, Any],
    baseline: list[dict[str, Any]],
    decode_owner: Callable[[bytes], Any],
    validate_owner_record: Callable[[Any], Any],
    validate_public_observations: Callable[[Any], Any],
    observe_snapshot: Callable[[], Any],
    observe_owner_after: Callable[[], Any],
    validate_owner_after: Callable[[Any], Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Validate a real zero-exit child while retaining every failure result."""
    failure_stage = "decode-owner-report"
    actual_owner_report: Mapping[str, Any] | None = None
    actual_public_observations: Mapping[str, Any] | None = None
    actual_snapshot: Mapping[str, Any] | None = None
    actual_owner_after: Mapping[str, Any] | None = None
    try:
        require(isinstance(retained_process, Mapping)
                and retained_process.get("role") == family
                and type(retained_process.get("returncode")) is int
                and retained_process.get("returncode") == 0,
                "the guarded candidate did not have a genuine zero exit code")
        stdout = restore_complete_stream(
            retained_process.get("stdout"),
            label=family + " exact zero-exit native owner stdout",
        )
        restore_complete_stream(
            retained_process.get("stderr"),
            label=family + " exact zero-exit native owner stderr",
        )
        decoded = decode_owner(stdout)
        require(isinstance(decoded, dict),
                "the real zero-exit native owner produced no complete document")
        actual_owner_report = decoded
        public = decoded.get("rebar_v19_guarded_public_surface")
        if isinstance(public, Mapping):
            actual_public_observations = public

        failure_stage = "validate-augmented-native-owner"
        validate_owner_record(decoded)

        failure_stage = "validate-complete-public-observations"
        observed = validate_public_observations(public)
        require(isinstance(observed, dict),
                "the complete actual public validation omitted its document")

        failure_stage = "validate-complete-original-worker-streams"
        validate_process_streams(
            retained_process,
            role=family,
            expected_document=decoded,
        )

        failure_stage = "validate-unmodified-original-native-owner"
        restored_owner = dict(decoded)
        restored_owner.pop("rebar_v19_guarded_public_surface", None)
        validate_owner_record(restored_owner)

        failure_stage = "validate-native-snapshot-after-matching"
        observed_snapshot = observe_snapshot()
        if isinstance(observed_snapshot, Mapping):
            actual_snapshot = observed_snapshot
        require(observed_snapshot == expected_snapshot,
                "the actual owned source or native binary changed inside matching")

        failure_stage = "observe-native-owner-after-matching"
        observed_after = observe_owner_after()
        if isinstance(observed_after, Mapping):
            actual_owner_after = observed_after

        failure_stage = "validate-native-owner-after-matching"
        after = validate_owner_after(observed_after)
        require(isinstance(after, dict),
                "the actual independent native owner after matching was omitted")
        actual_owner_after = after

        failure_stage = "validate-final-native-snapshot"
        final_snapshot = observe_snapshot()
        if isinstance(final_snapshot, Mapping):
            actual_snapshot = final_snapshot
        require(final_snapshot == expected_snapshot,
                "the genuine current owned candidate changed after matching")
        return decoded, observed, after
    except BaseException as error:
        raise PublicSurfaceV19WorkerFailure(
            family,
            "the complete zero-exit guarded native owner failed "
            + failure_stage,
            _zero_exit_guarded_failure_details(
                family,
                error,
                process=retained_process,
                owner_before=owner_before,
                composed_worker_sha256=composed_worker_sha256,
                failure_stage=failure_stage,
                baseline=baseline,
                actual_owner_report=actual_owner_report,
                actual_public_observations=actual_public_observations,
                actual_snapshot=actual_snapshot,
                actual_owner_after=actual_owner_after,
            ),
        ) from error


def run_guarded_candidate(
    family: str,
    *,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
    durable: Mapping[str, Any],
    baseline: list[dict[str, Any]],
) -> dict[str, Any]:
    owner = durable["owner"]
    v11 = durable["v11"]
    state = durable["families"][family]
    retry = durable["v12_retry"]["families"][family]
    snapshot = state["snapshot"]
    expected_native = snapshot["native_sha256_by_path"]
    require(v11.snapshot_family(family) == snapshot,
            "the current qualified source or native binary changed before work")
    before = v11.validate_owner(
        owner,
        owner.run_native_worker(family, dict(expected_native)),
        family,
        expected_native,
    )
    original = owner.NATIVE_OWNER_WORKER
    original_hash = owner.NATIVE_OWNER_WORKER_SHA256
    owner.validate_worker_source(original)
    composed, composed_hash = compose_guarded_owner(
        original, owner_source_sha256=original_hash,
    )
    owner.validate_worker_source(composed)
    configuration = _candidate_configuration(
        family,
        source_sha256=source_sha256,
        protocol_sha256=protocol_sha256,
        locales=locales,
        expected_native=expected_native,
    )
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
        "REBAR_PUBLIC_SURFACE_V19_CONTEXT": canonical(configuration).decode(
            "ascii",
        ),
    }
    if "LOCPATH" in os.environ:
        environment["LOCPATH"] = os.environ["LOCPATH"]
    arguments = [
        str(v17.PINNED_PYTHON), "-I", "-B", "-c", composed,
        str(ROOT), family, canonical(dict(expected_native)).decode("ascii"),
    ]
    try:
        process = subprocess.run(
            arguments,
            cwd=str(ROOT),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3_600,
        )
    except subprocess.TimeoutExpired as error:
        raise PublicSurfaceV19WorkerFailure(
            family,
            "the genuine same-process fully guarded native owner timed out",
            _timeout_failure_details(family, error, owner_before=before),
        ) from error
    except (OSError, subprocess.SubprocessError) as error:
        raise PublicSurfaceV19WorkerFailure(
            family,
            "the real same-process fully guarded native owner crashed",
            {"owner_before": before, **_error_details(error)},
        ) from error
    require(len(process.stdout) <= MAX_WORKER_BYTES
            and len(process.stderr) <= MAX_WORKER_BYTES,
            "the complete original guarded native streams exceed their bound")
    retained_process = {
        "role": family,
        "returncode": process.returncode,
        "stdout": capture_complete_stream(process.stdout),
        "stderr": capture_complete_stream(process.stderr),
    }
    if process.returncode != 0 or not process.stdout or process.stderr:
        details: dict[str, Any] = {
            "role": family,
            "returncode": process.returncode,
            "stdout": retained_process["stdout"],
            "stderr": retained_process["stderr"],
            "complete_original_worker_streams": retained_process,
            "owner_before": before,
            "composed_worker_sha256": composed_hash,
        }
        try:
            inner = _decode_guarded_stderr(process.stderr, family)
        except BaseException as decode_error:
            inner = None
            details["actual_failure_decode_error"] = _error_details(decode_error)
        if inner is not None:
            details["actual_guarded_failure"] = inner
            partial = inner.get("actual_failure_details")
            if isinstance(partial, dict):
                for name in (
                    "completed_records", "completed_count", "failure_stage",
                    "active_case", "locale_preflight", "actual_error",
                    "traceback",
                ):
                    if name in partial:
                        details[name] = partial[name]
        raise PublicSurfaceV19WorkerFailure(
            family,
            "the genuine same-process original native owner failed",
            details,
        )
    report, observed, after = validate_zero_exit_guarded_worker(
        family,
        retained_process=retained_process,
        owner_before=before,
        composed_worker_sha256=composed_hash,
        expected_snapshot=snapshot,
        baseline=baseline,
        decode_owner=lambda payload: owner.core.decode_report(
            payload,
            label="complete V19 public observations inside the exact V10 guard",
        ),
        validate_owner_record=lambda document: owner.validate_worker(
            document, family, dict(expected_native),
        ),
        validate_public_observations=lambda document: validate_embedded_records(
            document,
            family=family,
            source_sha256=source_sha256,
            protocol_sha256=protocol_sha256,
            expected_native=expected_native,
            baseline=baseline,
        ),
        observe_snapshot=lambda: v11.snapshot_family(family),
        observe_owner_after=lambda: owner.run_native_worker(
            family, dict(expected_native),
        ),
        validate_owner_after=lambda document: v11.validate_owner(
            owner, document, family, expected_native,
        ),
    )
    return {
        "schema": SCHEMA + "-candidate-worker",
        "status": "PASS",
        "family": family,
        "candidate_module": "candidates." + family + "_candidate",
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "native_sha256_by_path": dict(expected_native),
        "original_owner_worker_sha256": original_hash,
        "composed_owner_worker_sha256": composed_hash,
        "owner_before": before,
        "same_process_owner": report,
        "same_process_original_streams": retained_process,
        "public_observations": observed,
        "owner_after": after,
        "v11_edge_archive_sha256": state["edge"]["archive_sha256"],
        "v11_edge_proof_sha256": state["edge"]["proof_sha256"],
        "v11_deep_archive_sha256": state["deep"]["archive_sha256"],
        "v11_deep_proof_sha256": state["deep"]["proof_sha256"],
        "v12_deep_retry_proof_sha256": retry["proof_sha256"],
        "cases": EXPECTED_CASES,
        "record_sha256": observed["record_sha256"],
        "matched_inside_live_v10_owner_guard": True,
        "fresh_isolated_owner_checks": 2,
        "benchmark_or_timing_executed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
    }


def run_all_candidates(options: argparse.Namespace) -> dict[str, Any]:
    require(
        False,
        "BLOCKED: V19 is a candidate-independent CPython reference only; "
        + CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
    )
    base = authenticate_reference_prerequisites(
        options.source_sha256, options.protocol_sha256,
    )
    reference = authenticate_surface_reference(
        base,
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        reference_sha256=options.reference_sha256,
    )
    pins: dict[str, Any] = {
        "v10_base_report": options.v10_base_report_sha256,
        "v10_strict_report": options.v10_strict_report_sha256,
    }
    retry: dict[str, Any] = {}
    for family in FAMILIES:
        for kind in ("edge_archive", "edge_proof", "deep_archive", "deep_proof"):
            pins[family + "_" + kind] = getattr(
                options, family + "_" + kind + "_sha256",
            )
        retry[family + "_deep_retry_proof"] = getattr(
            options, family + "_deep_retry_proof_sha256",
        )
    durable = authenticate_durable_candidate_prerequisites(
        reference, pins, retry,
    )
    locales = _locale_names(options)
    _preflight_destinations((
        ALL_CANDIDATE_RELATIVE,
        ALL_CANDIDATE_FAILURE_RELATIVE,
        *CANDIDATE_FAILURE_RELATIVES.values(),
    ))
    completed: dict[str, dict[str, Any]] = {}
    active_family: str | None = None
    result: dict[str, Any] | None = None
    try:
        for family in FAMILIES:
            active_family = family
            completed[family] = run_guarded_candidate(
                family,
                source_sha256=options.source_sha256,
                protocol_sha256=options.protocol_sha256,
                locales=locales,
                durable=durable,
                baseline=reference["baseline_records"],
            )
            active_family = None
        require(set(completed) == set(FAMILIES),
                "an actually independently implemented candidate was omitted")
        result = {
            "schema": SCHEMA + "-all-candidates",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "v17_source_sha256": V17_SOURCE_SHA256,
            "v17_protocol_sha256": V17_PROTOCOL_SHA256,
            "v18_source_sha256": V18_SOURCE_SHA256,
            "v18_protocol_sha256": V18_PROTOCOL_SHA256,
            "v11_source_sha256": v18.V11_SOURCE_SHA256,
            "v11_protocol_sha256": v18.V11_PROTOCOL_SHA256,
            "v12_source_sha256": V12_SOURCE_SHA256,
            "v12_protocol_sha256": V12_PROTOCOL_SHA256,
            "v10_owner_source_sha256": v18.V10_OWNER_SHA256,
            "v10_strict_source_sha256": v18.V10_STRICT_SHA256,
            "v10_ownership_protocol_sha256":
                v18.V10_OWNERSHIP_PROTOCOL_SHA256,
            "v10_base_report_sha256": pins["v10_base_report"],
            "v10_strict_report_sha256": pins["v10_strict_report"],
            "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
            "v19_reference_sha256": reference["reference_sha256"],
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cohorts": EXPECTED_COHORTS,
            "cases_per_candidate": EXPECTED_CASES,
            "actual_candidate_checks": len(FAMILIES) * EXPECTED_CASES,
            "completed_families": list(FAMILIES),
            "genuine_durable_original_archive_count": 6,
            "genuine_v11_durable_owner_proof_count": 6,
            "genuine_v12_deep_retry_owner_proof_count": 3,
            "v12_retry_proof_sha256_by_family": {
                family: durable["v12_retry"]["families"][family]["proof_sha256"]
                for family in FAMILIES
            },
            "fresh_isolated_owner_checks_per_family": 2,
            "matching_inside_live_original_owner_guard": True,
            "candidate_records": completed,
            "failure_records": [],
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        exclusive_write(result, ALL_CANDIDATE_RELATIVE)
        return result
    except BaseException as error:
        if isinstance(error, PublicSurfaceV19WorkerFailure):
            family: str | None = error.role
        elif active_family is not None:
            family = active_family
        else:
            family = None
        if family is None:
            failure = {
                "schema": SCHEMA + "-all-candidates-failure",
                "status": "FAIL",
                "synthetic": False,
                "failure_scope": (
                    "all-family-report-publication"
                    if result is not None else "all-family-validation"
                ),
                "failed_family": None,
                "completed_families": completed,
                "completed_family_count": len(completed),
                "complete_unpublished_passing_result": result,
                **_error_details(error),
                "holdout_cases_read": 0,
                "performance_fixtures_read": 0,
                "benchmark_or_timing_executed": False,
                "performance": "NOT MEASURED",
            }
            exclusive_write(failure, ALL_CANDIDATE_FAILURE_RELATIVE)
        else:
            failure = {
                "schema": SCHEMA + "-candidate-failure",
                "status": "FAIL",
                "synthetic": False,
                "failure_scope": "candidate-family",
                "failed_family": family,
                "completed_families": completed,
                **_error_details(error),
                "holdout_cases_read": 0,
                "performance_fixtures_read": 0,
                "benchmark_or_timing_executed": False,
                "performance": "NOT MEASURED",
            }
            if isinstance(error, PublicSurfaceV19WorkerFailure):
                failure["actual_failure_details"] = error.details
            exclusive_write(failure, CANDIDATE_FAILURE_RELATIVES[family])
        raise


def _synthetic_configuration(family: str = "rust") -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-embedded-configuration",
        "family": family,
        "source_sha256": "a" * 64,
        "protocol_sha256": "b" * 64,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v18_source_sha256": V18_SOURCE_SHA256,
        "v18_protocol_sha256": V18_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "iso8859_1_locale": "source-only-iso8859-1",
        "utf8_locale": "source-only-utf8",
        "expected_native_sha256": {
            "candidates/source-only-synthetic-owner.so": "c" * 64,
        },
    }


def _synthetic_audited_graph() -> tuple[
    dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]],
]:
    """Pure in-memory 7+2+3 source and 2+1+2 native graph controls."""
    counts = {"rust": (7, 2), "vm": (2, 1), "zig": (3, 2)}
    specifications: dict[str, dict[str, Any]] = {}
    snapshots: dict[str, dict[str, Any]] = {}
    all_sources: dict[str, str] = {}
    all_native: dict[str, str] = {}
    for family in FAMILIES:
        source_count, native_count = counts[family]
        sources = tuple(
            "source-only-owned/" + family + "/source-" + str(index) + ".txt"
            for index in range(source_count)
        )
        native = {
            "role-" + str(index):
                "source-only-owned/" + family + "/native-" + str(index) + ".elf"
            for index in range(native_count)
        }
        source_hashes = {
            relative: hashlib.sha256(
                ("source-only-owned-source:" + relative).encode("ascii"),
            ).hexdigest()
            for relative in sources
        }
        native_hashes = {
            relative: hashlib.sha256(
                ("source-only-owned-native:" + relative).encode("ascii"),
            ).hexdigest()
            for relative in native.values()
        }
        specifications[family] = {
            "module": "candidates." + family + "_candidate",
            "contract_name": CONTRACT_NAMES[family],
            "sources": sources,
            "native": native,
        }
        snapshots[family] = {
            "family": family,
            "module": "candidates." + family + "_candidate",
            "source_sha256_by_path": source_hashes,
            "native_sha256_by_path": native_hashes,
        }
        all_sources.update(source_hashes)
        all_native.update(native_hashes)
    return {
        "all_family_audit_qualified": True,
        "all_family_source_sha256_by_path": all_sources,
        "all_family_native_elf_sha256_by_path": all_native,
    }, snapshots, specifications


class _SourceOnlyProducerCodec:
    """In-memory pretty-byte control; never loads a V11/V12 validator."""

    @staticmethod
    def decode_json(payload: bytes, label: str) -> dict[str, Any]:
        try:
            document = json.loads(
                payload.decode("ascii"),
                object_pairs_hook=v17._unique_json_pairs,
                parse_constant=lambda actual: (_ for _ in ()).throw(
                    PublicSurfaceV19Error(
                        "a source-only producer proof contains " + actual,
                    ),
                ),
            )
        except (ValueError, UnicodeError, json.JSONDecodeError) as error:
            raise PublicSurfaceV19Error(
                "a source-only complete producer proof is malformed: " + label,
            ) from error
        require(isinstance(document, dict),
                "a source-only producer proof is not an object: " + label)
        return document

    @staticmethod
    def canonical(document: Mapping[str, Any]) -> bytes:
        return (
            json.dumps(
                document,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                indent=2,
            )
            + "\n"
        ).encode("ascii")


def _source_error() -> BaseException:
    try:
        raise ValueError("source-only actual inner public failure")
    except ValueError as error:
        return error


def _synthetic_reference_failure(
    role: str,
    matrix: list[dict[str, Any]],
    *,
    prefix_count: int = 0,
    failure_stage: str = "case",
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for row in matrix[:prefix_count]:
        if row["cohort"] in {
            "real-locale-switch-on-compiled-bytes",
            "real-locale-invalid-flags-and-cache",
        }:
            transitions = []
            for name, codeset, high in (
                ("iso8859_1", "latin1", True),
                ("utf8", "utf8", False),
                ("iso8859_1_again", "latin1", True),
            ):
                transitions.append({
                    "locale": name,
                    "codeset": codeset,
                    "same_compiled_pattern": True,
                    "ascii_byte": "source-only",
                    "high_byte": "source-only" if high else None,
                    "scanner": "source-only" if high else None,
                })
            outcome = {
                "status": "return",
                "value": normalize({
                    "transitions": transitions,
                    "purge_recreates": True,
                    "purge_match": "source-only",
                    "locale_with_text": {"status": "raise"},
                    "locale_with_ascii": {"status": "raise"},
                }),
            }
        else:
            outcome = {"status": "return", "value": "source-only"}
        records.append({
            "id": row["id"],
            "cohort": row["cohort"],
            "stimulus_sha256": digest(v17.build_stimulus(row)),
            "outcome": outcome,
        })
    preflight = (
        None
        if failure_stage == "preflight"
        else {
            "iso8859_1_codeset": "latin1",
            "utf8_codeset": "utf8",
            "ctype_restored": True,
            "locale_path_unchanged": True,
        }
    )
    return _reference_failure_document(
        role=role,
        source_sha256="a" * 64,
        protocol_sha256="b" * 64,
        locale_names={
            "iso8859_1": "source-only-iso8859-1",
            "utf8": "source-only-utf8",
        },
        locale_preflight=preflight,
        completed_records=records,
        failure_stage=failure_stage,
        active_case=(
            matrix[prefix_count]["id"]
            if failure_stage == "case" and prefix_count < EXPECTED_CASES
            else None
        ),
        error=_source_error(),
    )


def _source_only_zero_exit_guarded_worker(
    family: str,
    baseline: list[dict[str, Any]],
    snapshot: Mapping[str, Any],
    *,
    mode: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Exercise the real failure transport entirely on in-memory records."""
    require(mode in {
        "pass", "malformed", "mismatch", "augmented-owner",
        "restored-owner", "snapshot", "owner-after", "final-snapshot",
    }, "an actual source-only zero-exit poison was substituted")
    actual_records = copy.deepcopy(baseline)
    if mode == "mismatch":
        actual_records[14]["outcome"] = {
            "status": "return",
            "value": "source-only genuine public mismatch",
        }
    actual_public = {
        "schema": "source-only-v19-actual-public-observations",
        "status": "PASS",
        "records": actual_records,
    }
    actual_owner = {
        "schema": "source-only-v19-actual-native-owner",
        "status": "PASS",
        "rebar_v19_guarded_public_surface": actual_public,
    }
    original_stdout = (
        b'{"source-only-malformed-zero-exit":'
        if mode == "malformed"
        else canonical(actual_owner) + b"\n"
    )
    retained_process = {
        "role": family,
        "returncode": 0,
        "stdout": capture_complete_stream(original_stdout),
        "stderr": capture_complete_stream(b""),
    }
    before = {
        "schema": "source-only-v19-actual-owner-before",
        "family": family,
        "status": "PASS",
    }
    composed_hash = hashlib.sha256(
        ("source-only-v19-real-zero-exit-owner:" + family).encode("ascii"),
    ).hexdigest()
    snapshot_calls = [0]

    def decode(payload: bytes) -> dict[str, Any]:
        return strict_canonical(payload, "source-only original zero-exit owner")

    def validate_owner(document: Any) -> Any:
        require(isinstance(document, dict)
                and document.get("status") == "PASS",
                "the source-only actual native owner was malformed")
        augmented = "rebar_v19_guarded_public_surface" in document
        require(not (mode == "augmented-owner" and augmented),
                "the source-only actual augmented native owner failed")
        require(not (mode == "restored-owner" and not augmented),
                "the source-only actual restored native owner failed")
        return document

    def validate_public(document: Any) -> Any:
        require(isinstance(document, Mapping)
                and document.get("status") == "PASS"
                and document.get("records") == baseline,
                "the source-only actual complete public records mismatch")
        return dict(document)

    def observe_snapshot() -> dict[str, Any]:
        snapshot_calls[0] += 1
        actual = copy.deepcopy(dict(snapshot))
        if ((mode == "snapshot" and snapshot_calls[0] == 1)
                or (mode == "final-snapshot" and snapshot_calls[0] == 2)):
            sources = actual.get("source_sha256_by_path")
            if isinstance(sources, dict) and sources:
                first = next(iter(sources))
                sources[first] = "0" * 64
        return actual

    def observe_after() -> dict[str, Any]:
        return {
            "schema": "source-only-v19-actual-owner-after",
            "status": "FAIL" if mode == "owner-after" else "PASS",
            "family": family,
        }

    def validate_after(actual: Any) -> dict[str, Any]:
        require(isinstance(actual, dict) and actual.get("status") == "PASS",
                "the source-only actual native owner after matching failed")
        return actual

    return validate_zero_exit_guarded_worker(
        family,
        retained_process=retained_process,
        owner_before=before,
        composed_worker_sha256=composed_hash,
        expected_snapshot=snapshot,
        baseline=baseline,
        decode_owner=decode,
        validate_owner_record=validate_owner,
        validate_public_observations=validate_public,
        observe_snapshot=observe_snapshot,
        observe_owner_after=observe_after,
        validate_owner_after=validate_after,
    )


def self_test() -> dict[str, Any]:
    verify_runtime()
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate was imported before source-only public controls")
    # Exactly four declared, immutable instruction files; no campaign, failure,
    # audit, candidate, performance case, report, V12 file, or holdout is read.
    authenticate_frozen_predecessors()
    inherited = v18.self_test()
    require(
        inherited.get("status") == "PASS"
        and inherited.get("check_count", 0) >= 250
        and inherited.get("inherited_v17_check_count", 0) >= 336
        and inherited.get("total_independent_source_controls", 0) >= 586
        and inherited.get("cases") == EXPECTED_CASES
        and inherited.get("cohorts") == EXPECTED_COHORTS
        and inherited.get("matrix_sha256") == MATRIX_SHA256
        and inherited.get("stimulus_sha256") == STIMULUS_SHA256
        and inherited.get("candidate_source_files_read") == 0
        and inherited.get("evidence_files_read") == 0
        and inherited.get("files_written") == 0
        and inherited.get("candidate_imports") == 0
        and inherited.get("subprocesses") == 0
        and inherited.get("threads_started") == 0
        and inherited.get("clock_samples") == 0
        and inherited.get("entropy_draws") == 0
        and inherited.get("locale_changes") == 0
        and inherited.get("regex_matching_calls") == 0
        and inherited.get("holdout_cases_read") == 0
        and inherited.get("performance_fixtures_read") == 0
        and inherited.get("benchmark_or_timing_executed") is False,
        "the complete immutable V17 and V18 source-only poison controls failed",
    )
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "a V19 source-only control was counted more than once")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (
            PublicSurfaceV19Error, v17.PublicSurfaceError,
            v18.PublicSurfaceV18Error, AssertionError, ValueError,
            TypeError, KeyError, SyntaxError, UnicodeError,
        ):
            check(name, True)
        else:
            check(name, False)

    with v17._source_only_effects() as effects:
        matrix = build_matrix()
        check("retain-all-actual-v17-and-v18-source-only-poisons",
              inherited["total_independent_source_controls"] >= 586)
        check("preserve-all-1376-exact-independent-public-cases",
              len(matrix) == EXPECTED_CASES)
        check("preserve-the-exact-frozen-public-matrix",
              v17.validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
              == MATRIX_SHA256)
        check("preserve-the-exact-frozen-behavioral-stimuli",
              v17.validate_stimuli(matrix, expected_sha256=STIMULUS_SHA256)
              ["stimulus_sha256"] == STIMULUS_SHA256)
        check("preserve-the-real-v18-failure-without-opening-it",
              valid_sha256(V18_HISTORICAL_FAILURE_SHA256)
              and V18_HISTORICAL_FAILURE_RELATIVE
              not in APPROVED_OUTPUTS)
        check("declare-repaired-current-graph-candidates-truthfully-blocked",
              CURRENT_GRAPH_CANDIDATE_QUALIFICATION == "BLOCKED"
              and CURRENT_GRAPH_CANDIDATE_EVIDENCE == "NOT QUALIFIED"
              and "V13" in CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON
              and "V14" in CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON
              and "V20" in CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON)
        reject("reject-current-graph-candidate-cli-before-any-proof-or-worker",
               lambda: run_all_candidates(argparse.Namespace()))
        check("never-guess-a-future-v13-current-graph-source-hash",
              "V13_SOURCE_SHA256" not in globals()
              and "V13_PROTOCOL_SHA256" not in globals())
        check("never-guess-a-future-v14-current-graph-proof-hash",
              "V14_SOURCE_SHA256" not in globals()
              and "V14_PROTOCOL_SHA256" not in globals())
        check("never-claim-an-unfrozen-current-graph-v20-candidate-pass",
              "V20_SOURCE_SHA256" not in globals()
              and "V20_PROTOCOL_SHA256" not in globals())
        check("require-the-authenticated-original-152-python-methods",
              v17.PRIVATE_CONDITIONAL_METHOD == "ReTests.test_memory_leaks")
        check("require-31-genuine-ordered-python-public-exports",
              len(v17.PUBLIC_EXPORTS) == 31)
        check("require-13-genuine-python-public-pattern-members",
              len(v17.PUBLIC_PATTERN_MEMBERS) == 13)
        check("require-14-genuine-python-public-match-members",
              len(v17.PUBLIC_MATCH_MEMBERS) == 14)
        check("pin-independent-published-v17-source-and-protocol",
              V17_SOURCE_SHA256 != V17_PROTOCOL_SHA256)
        check("pin-independent-published-v18-source-and-protocol",
              V18_SOURCE_SHA256 != V18_PROTOCOL_SHA256)
        check("pin-independent-reviewed-v12-source-and-protocol",
              V12_SOURCE_SHA256 != V12_PROTOCOL_SHA256)
        check("never-reuse-v18-passing-or-failure-output",
              not (set(APPROVED_OUTPUTS) & set(v18.APPROVED_OUTPUTS)))
        check("keep-all-family-publication-failures-separate-from-zig",
              ALL_CANDIDATE_FAILURE_RELATIVE in APPROVED_OUTPUTS
              and ALL_CANDIDATE_FAILURE_RELATIVE != ALL_CANDIDATE_RELATIVE
              and ALL_CANDIDATE_FAILURE_RELATIVE
              not in CANDIDATE_FAILURE_RELATIVES.values())
        check("bind-evidence-publication-to-a-no-follow-directory-descriptor",
              {"fstat", "stat", "open", "close", "fsync"}
              <= set(exclusive_write.__code__.co_names)
              and {"O_DIRECTORY", "O_NOFOLLOW"}
              <= {
                  item for item in exclusive_write.__code__.co_consts
                  if type(item) is str
              }
              and "directory" in exclusive_write.__code__.co_varnames)

        for cohort in v17.COHORTS:
            rows = [row for row in matrix if row["cohort"] == cohort]
            stimuli = [v17.build_stimulus(row) for row in rows]
            check("retain-32-exact-frozen-rows-" + cohort, len(rows) == 32)
            check("retain-32-distinct-public-stimuli-" + cohort,
                  len({digest(stimulus) for stimulus in stimuli}) == 32)
            check("retain-32-distinct-actual-expressions-" + cohort,
                  len({stimulus["expression"] for stimulus in stimuli}) == 32)
            check("retain-32-distinct-actual-subjects-" + cohort,
                  len({stimulus["subject"] for stimulus in stimuli}) == 32)

        for symbol in v17.PUBLIC_EXPORTS:
            check("retain-original-public-export-" + symbol,
                  v17.PUBLIC_EXPORTS.count(symbol) == 1)
        for member in v17.PUBLIC_PATTERN_MEMBERS:
            check("retain-original-public-pattern-member-" + member,
                  v17.PUBLIC_PATTERN_MEMBERS.count(member) == 1)
        for member in v17.PUBLIC_MATCH_MEMBERS:
            check("retain-original-public-match-member-" + member,
                  v17.PUBLIC_MATCH_MEMBERS.count(member) == 1)

        for index, value in enumerate((
            None, True, False, 0, -1, 2**128, "", "plain public result",
        )):
            check("preserve-exact-public-scalar-" + str(index),
                  normalize(value) == value)
        for name, value, expected in (
            ("finite-float", 1.25,
             {"kind": "float", "hex": 1.25.hex()}),
            ("negative-float", -0.0,
             {"kind": "float", "hex": (-0.0).hex()}),
            ("bytes", b"\x00\xff",
             {"kind": "bytes", "hex": "00ff"}),
            ("bytearray", bytearray(b"\x00\xff"),
             {"kind": "bytearray", "hex": "00ff"}),
            ("list", ["x", 1],
             {"kind": "list", "items": ["x", 1]}),
            ("tuple", ("x", 1),
             {"kind": "tuple", "items": ["x", 1]}),
            ("set", {"b", "a"},
             {"kind": "set", "items": ["a", "b"]}),
            ("frozenset", frozenset({"b", "a"}),
             {"kind": "frozenset", "items": ["a", "b"]}),
            ("type", ValueError,
             {"kind": "type", "name": "ValueError"}),
        ):
            actual = normalize(value)
            check("retain-exact-normalized-public-shape-" + name,
                  actual == expected and isinstance(actual, _NormalizedEnvelope))
            check("make-only-authentic-v19-envelopes-idempotent-" + name,
                  normalize(actual) is actual)

        ascending = normalize({"b": 2, "a": 1})
        descending = normalize({"a": 1, "b": 2})
        check("canonicalize-real-public-mapping-key-order",
              ascending == descending
              and ascending == {
                  "kind": "mapping",
                  "items": [["a", 1], ["b", 2]],
              })
        impersonator = {"kind": "mapping", "items": [["a", 1]]}
        actual_impersonator = normalize(impersonator)
        check("never-trust-an-ordinary-envelope-lookalike",
              actual_impersonator is not impersonator
              and actual_impersonator["kind"] == "mapping"
              and any(pair[0] == "kind"
                      for pair in actual_impersonator["items"]))
        external_envelope = _NormalizedEnvelope(
            {"kind": "mapping", "items": [["forged", True]]},
        )
        observed_external = normalize(external_envelope)
        check("reject-an-externally-constructed-private-envelope",
              observed_external is not external_envelope
              and observed_external["kind"] == "mapping"
              and any(pair[0] == "kind"
                      for pair in observed_external["items"]))

        class _ForgedEnvelope(_NormalizedEnvelope):
            pass

        forged_subclass = _ForgedEnvelope(
            {"kind": "mapping", "items": [["forged-subclass", True]]},
        )
        observed_subclass = normalize(forged_subclass)
        check("reject-an-externally-constructed-private-envelope-subclass",
              observed_subclass is not forged_subclass
              and observed_subclass["kind"] == "mapping"
              and any(pair[0] == "kind"
                      for pair in observed_subclass["items"]))
        actual_private = _new_normalized_envelope(
            kind="source-only-authentic-envelope",
        )
        check("authenticate-the-actual-private-envelope-creator-identity",
              type(actual_private) is _NormalizedEnvelope
              and _AUTHENTIC_NORMALIZED_ENVELOPES.get(id(actual_private))
              is actual_private
              and normalize(actual_private) is actual_private)
        check("distinguish-a-real-list-from-a-public-tuple",
              normalize([1]) != normalize((1,)))
        check("distinguish-real-bytes-from-a-mutable-bytearray",
              normalize(b"a") != normalize(bytearray(b"a")))

        deep: list[Any] = []
        cursor = deep
        for _ in range(512):
            next_item: list[Any] = []
            cursor.append(next_item)
            cursor = next_item
        normalized_deep = normalize(deep)
        observed_depth = 0
        cursor_result: Any = normalized_deep
        while cursor_result.get("items"):
            observed_depth += 1
            cursor_result = cursor_result["items"][0]
        check("accept-finite-acyclic-public-structure-beyond-v17-depth-24",
              observed_depth == 512)
        check("normalize-finite-deep-public-observations-without-recursion",
              normalized_deep["kind"] == "list"
              and cursor_result == {"kind": "list", "items": []})

        direct_cycle: list[Any] = []
        direct_cycle.append(direct_cycle)
        actual_cycle = normalize(direct_cycle)
        check("detect-a-true-list-cycle-by-object-identity",
              actual_cycle == {
                  "kind": "list",
                  "items": [{"kind": "reference", "index": 0}],
              })
        mapping_cycle: dict[str, Any] = {}
        mapping_cycle["self"] = mapping_cycle
        check("detect-a-true-mapping-cycle-by-object-identity",
              normalize(mapping_cycle) == {
                  "kind": "mapping",
                  "items": [["self", {"kind": "reference", "index": 0}]],
              })
        mixed_cycle: dict[str, Any] = {"child": []}
        mixed_cycle["child"].append(mixed_cycle)
        check("detect-a-real-mixed-list-mapping-cycle",
              normalize(mixed_cycle) == {
                  "kind": "mapping",
                  "items": [["child", {
                      "kind": "list",
                      "items": [{"kind": "reference", "index": 0}],
                  }]],
              })
        shared = ["actual shared structure"]
        shared_value = normalize([shared, shared])
        check("retain-true-shared-public-object-identity",
              shared_value == {
                  "kind": "list",
                  "items": [
                      {"kind": "list", "items": ["actual shared structure"]},
                      {"kind": "reference", "index": 1},
                  ],
              })
        check("never-label-equal-distinct-public-objects-as-shared",
              normalize([["same"], ["same"]]) == {
                  "kind": "list",
                  "items": [
                      {"kind": "list", "items": ["same"]},
                      {"kind": "list", "items": ["same"]},
                  ],
              })
        exception_cycle = ValueError("source-only genuine exception cycle")
        exception_cycle.__cause__ = exception_cycle
        normalized_exception_cycle = normalize(exception_cycle)
        check("detect-a-real-self-referential-public-exception-cause",
              normalized_exception_cycle.get("kind") == "exception"
              and normalized_exception_cycle.get("type") == "ValueError"
              and normalized_exception_cycle.get("cause")
              == {"kind": "reference", "index": 0})

        repeated = normalize({"actual": ["public", "result"]})
        for index in range(40):
            prior = repeated
            repeated = normalize(repeated)
            check("avoid-actual-v18-double-normalization-failure-"
                  + str(index), repeated is prior)
        original_normalize = v17.normalize
        with cycle_safe_normalization():
            check("install-exact-source-authenticated-cycle-safe-normalizer",
                  v17.normalize is normalize)
            inner = v17.normalize({"public": ["valid", "finite"]})
            for index in range(32):
                previous = inner
                inner = v17.normalize(inner)
                check("preserve-repeated-frozen-v17-normalize-call-"
                      + str(index), inner is previous)
        check("restore-exact-original-immutable-v17-normalizer",
              v17.normalize is original_normalize)
        try:
            with cycle_safe_normalization():
                raise ValueError("source-only reversible normalization poison")
        except ValueError:
            check("restore-frozen-normalizer-after-an-actual-exception",
                  v17.normalize is original_normalize)
        reject("reject-a-forged-negative-public-normalization-depth",
               lambda: normalize("source-only", depth=-1))
        reject("reject-a-bool-masquerading-as-normalization-depth",
               lambda: normalize("source-only", depth=True))

        codec = _SourceOnlyProducerCodec()
        producer_document = {
            "schema": "source-only-v19-actual-pretty-producer",
            "status": "PASS",
            "nested": {"alpha": 1, "beta": ["genuine", "bytes"]},
        }
        producer_raw = codec.canonical(producer_document)
        check("retain-genuine-v11-v12-pretty-canonical-producer-bytes",
              decode_producer_canonical(
                  producer_raw, "source-only-producer", codec,
              ) == producer_document
              and producer_raw != canonical(producer_document) + b"\n")
        reject("reject-compact-json-for-a-pretty-canonical-v11-v12-proof",
               lambda: decode_producer_canonical(
                   canonical(producer_document) + b"\n",
                   "source-only-substituted-compact-producer",
                   codec,
               ))
        reject("reject-a-truncated-original-pretty-canonical-proof",
               lambda: decode_producer_canonical(
                   producer_raw[:-2],
                   "source-only-truncated-producer",
                   codec,
               ))
        reject("reject-duplicated-keys-in-original-producer-proof",
               lambda: decode_producer_canonical(
                   b'{"source_only":1,"source_only":2}\n',
                   "source-only-duplicate-producer",
                   codec,
               ))
        reject("reject-pretty-producer-bytes-as-compact-worker-json",
               lambda: strict_canonical(
                   producer_raw, "source-only-wrong-worker-encoding",
               ))

        source_graph, source_snapshots, source_specifications = (
            _synthetic_audited_graph()
        )
        check("bind-all-twelve-owned-source-hashes-to-both-v10-audits",
              validate_audited_graph_identity(
                  source_graph, source_snapshots, source_specifications,
              ) is source_graph
              and len(source_graph["all_family_source_sha256_by_path"]) == 12)
        check("bind-all-five-native-elf-hashes-to-both-v10-audits",
              len(source_graph["all_family_native_elf_sha256_by_path"]) == 5)
        for family in FAMILIES:
            for index, path in enumerate(
                source_specifications[family]["sources"],
            ):
                changed_graph = copy.deepcopy(source_graph)
                changed_graph["all_family_source_sha256_by_path"][path] = (
                    "0" * 64
                )
                reject("reject-current-v10-audited-source-hash-"
                       + family + "-" + str(index),
                       lambda changed_graph=changed_graph:
                       validate_audited_graph_identity(
                           changed_graph, source_snapshots, source_specifications,
                       ))
                changed_snapshot = copy.deepcopy(source_snapshots)
                changed_snapshot[family]["source_sha256_by_path"][path] = (
                    "0" * 64
                )
                reject("reject-current-family-snapshot-source-hash-"
                       + family + "-" + str(index),
                       lambda changed_snapshot=changed_snapshot:
                       validate_audited_graph_identity(
                           source_graph, changed_snapshot, source_specifications,
                       ))
                missing_snapshot = copy.deepcopy(source_snapshots)
                missing_snapshot[family]["source_sha256_by_path"].pop(path)
                reject("reject-missing-owned-family-source-path-"
                       + family + "-" + str(index),
                       lambda missing_snapshot=missing_snapshot:
                       validate_audited_graph_identity(
                           source_graph, missing_snapshot,
                           source_specifications,
                       ))
            for index, path in enumerate(
                source_specifications[family]["native"].values(),
            ):
                changed_native = copy.deepcopy(source_graph)
                changed_native["all_family_native_elf_sha256_by_path"][path] = (
                    "0" * 64
                )
                reject("reject-current-v10-audited-native-hash-"
                       + family + "-" + str(index),
                       lambda changed_native=changed_native:
                       validate_audited_graph_identity(
                           changed_native, source_snapshots,
                           source_specifications,
                       ))
                changed_snapshot = copy.deepcopy(source_snapshots)
                changed_snapshot[family]["native_sha256_by_path"][path] = (
                    "0" * 64
                )
                reject("reject-current-family-snapshot-native-hash-"
                       + family + "-" + str(index),
                       lambda changed_snapshot=changed_snapshot:
                       validate_audited_graph_identity(
                           source_graph, changed_snapshot,
                           source_specifications,
                       ))
                missing_snapshot = copy.deepcopy(source_snapshots)
                missing_snapshot[family]["native_sha256_by_path"].pop(path)
                reject("reject-missing-owned-family-native-path-"
                       + family + "-" + str(index),
                       lambda missing_snapshot=missing_snapshot:
                       validate_audited_graph_identity(
                           source_graph, missing_snapshot,
                           source_specifications,
                       ))
        for family in FAMILIES:
            missing_family = copy.deepcopy(source_snapshots)
            missing_family.pop(family)
            reject("reject-missing-complete-independent-owned-family-" + family,
                   lambda missing_family=missing_family:
                   validate_audited_graph_identity(
                       source_graph, missing_family, source_specifications,
                   ))
        for field in (
            "all_family_source_sha256_by_path",
            "all_family_native_elf_sha256_by_path",
        ):
            missing_graph = copy.deepcopy(source_graph)
            missing_graph[field].popitem()
            reject("reject-missing-complete-real-owned-audit-graph-" + field,
                   lambda missing_graph=missing_graph:
                   validate_audited_graph_identity(
                       missing_graph, source_snapshots, source_specifications,
                   ))

        source_baseline = _synthetic_reference_failure(
            "reference_a",
            matrix,
            prefix_count=EXPECTED_CASES,
            failure_stage="postflight",
        )["completed_records"]
        source_snapshot = source_snapshots["rust"]
        successful_owner, successful_public, successful_after = (
            _source_only_zero_exit_guarded_worker(
                "rust", source_baseline, source_snapshot, mode="pass",
            )
        )
        check("validate-actual-source-only-complete-zero-exit-owner",
              successful_owner["status"] == "PASS"
              and successful_public["records"] == source_baseline
              and len(successful_public["records"]) == EXPECTED_CASES
              and successful_after["status"] == "PASS")
        for mode, expected_stage in (
            ("malformed", "decode-owner-report"),
            ("mismatch", "validate-complete-public-observations"),
            ("augmented-owner", "validate-augmented-native-owner"),
            ("restored-owner", "validate-unmodified-original-native-owner"),
            ("snapshot", "validate-native-snapshot-after-matching"),
            ("owner-after", "validate-native-owner-after-matching"),
            ("final-snapshot", "validate-final-native-snapshot"),
        ):
            try:
                _source_only_zero_exit_guarded_worker(
                    "rust", source_baseline, source_snapshot, mode=mode,
                )
            except PublicSurfaceV19WorkerFailure as actual_failure:
                details = actual_failure.details
                retained = details.get("complete_original_worker_streams")
                check("preserve-zero-exit-complete-child-evidence-" + mode,
                      actual_failure.role == "rust"
                      and details.get("role") == "rust"
                      and type(details.get("returncode")) is int
                      and details["returncode"] == 0
                      and details.get("failure_stage") == expected_stage
                      and isinstance(retained, dict)
                      and retained.get("role") == "rust"
                      and type(retained.get("returncode")) is int
                      and retained["returncode"] == 0
                      and details.get("stdout") == retained.get("stdout")
                      and details.get("stderr") == retained.get("stderr")
                      and restore_complete_stream(
                          retained["stderr"],
                          label="source-only genuine zero-exit failure stderr",
                      ) == b""
                      and isinstance(details.get("owner_before"), dict)
                      and details["owner_before"].get("status") == "PASS"
                      and valid_sha256(details.get("composed_worker_sha256"))
                      and isinstance(details.get("actual_error"), dict)
                      and type(details.get("traceback")) is str
                      and bool(details["traceback"]))
                if mode == "malformed":
                    check("preserve-malformed-zero-exit-without-inventing-report",
                          restore_complete_stream(
                              retained["stdout"],
                              label="source-only genuine malformed owner bytes",
                          ) == b'{"source-only-malformed-zero-exit":'
                          and "actual_decoded_owner_report" not in details
                          and "actual_embedded_public_observations"
                          not in details
                          and "completed_records" not in details
                          and "first_actual_public_mismatch" not in details)
                else:
                    check("preserve-all-1376-zero-exit-public-results-" + mode,
                          isinstance(details.get("actual_decoded_owner_report"),
                                     dict)
                          and isinstance(
                              details.get("actual_embedded_public_observations"),
                              dict,
                          )
                          and details.get("completed_count") == EXPECTED_CASES
                          and isinstance(details.get("completed_records"), list)
                          and len(details["completed_records"]) == EXPECTED_CASES
                          and restore_complete_stream(
                              retained["stdout"],
                              label="source-only genuine complete owner bytes",
                          ) == canonical(
                              details["actual_decoded_owner_report"],
                          ) + b"\n")
                if mode == "mismatch":
                    first = details.get("first_actual_public_mismatch")
                    check("preserve-first-real-zero-exit-public-mismatch",
                          isinstance(first, dict)
                          and first.get("index") == 14
                          and first.get("case_id") == matrix[14]["id"]
                          and first.get("expected_record")
                          == source_baseline[14]
                          and first.get("actual_record")
                          == details["completed_records"][14]
                          and first["actual_record"]
                          != first["expected_record"])
                if mode == "owner-after":
                    check("preserve-actual-zero-exit-failed-post-owner-record",
                          isinstance(details.get("actual_observed_owner_after"),
                                     dict)
                          and details["actual_observed_owner_after"]
                          .get("status") == "FAIL")
                if mode in {"snapshot", "final-snapshot"}:
                    check("preserve-actual-zero-exit-changed-source-snapshot-"
                          + mode,
                          isinstance(
                              details.get("actual_observed_family_snapshot"),
                              dict,
                          )
                          and details["actual_observed_family_snapshot"]
                          != source_snapshot)
            else:
                check("preserve-zero-exit-complete-child-evidence-" + mode,
                      False)

        source_owner = v18._synthetic_owner_source()
        owner_hash = hashlib.sha256(source_owner.encode("utf-8")).hexdigest()
        composed, composed_hash = compose_guarded_owner(
            source_owner, owner_source_sha256=owner_hash,
        )
        check("parse-the-original-fully-guarded-synthetic-v10-owner",
              isinstance(ast.parse(composed), ast.Module))
        check("preserve-the-exact-frozen-original-native-owner-hash",
              hashlib.sha256(source_owner.encode("utf-8")).hexdigest()
              == owner_hash)
        check("derive-a-genuine-distinct-composed-owner-fingerprint",
              valid_sha256(composed_hash) and composed_hash != owner_hash)
        check("preload-v19-before-the-real-cached-matcher-poison",
              composed.count(PRELOAD_INJECTION) == 1
              and composed.index(PRELOAD_INJECTION)
              < composed.index(PRELOAD_MARKER))
        check("run-v19-exactly-once-inside-the-original-live-guard",
              composed.count(OBSERVATION_INJECTION) == 1
              and composed.index(OBSERVATION_INJECTION)
              < composed.index(AFTER_GUARD_MARKER))
        check("retain-the-original-complete-native-owner-observation",
              composed.count(OWNER_RECORD_INJECTION) == 1
              and composed.count(OWNER_RECORD_MARKER) == 1)
        check("preserve-a-full-actual-guarded-inner-failure",
              "guarded_failure_document" in OBSERVATION_INJECTION
              and "sys.stderr.write" in OBSERVATION_INJECTION)
        check("never-import-a-candidate-from-the-public-injection",
              "import candidates" not in PRELOAD_INJECTION
              and "import candidates" not in OBSERVATION_INJECTION
              and "sys.modules.get(_rebar19_candidate_name)"
              in OBSERVATION_INJECTION)
        for name, marker in (
            ("preload-before-original-guard", PRELOAD_MARKER),
            ("match-inside-original-guard", AFTER_GUARD_MARKER),
            ("retain-complete-original-owner", OWNER_RECORD_MARKER),
        ):
            removed = source_owner.replace(marker, "", 1)
            removed_hash = hashlib.sha256(removed.encode("utf-8")).hexdigest()
            reject("reject-missing-actual-native-owner-marker-" + name,
                   lambda removed=removed, removed_hash=removed_hash:
                   compose_guarded_owner(
                       removed, owner_source_sha256=removed_hash,
                   ))
            duplicated = source_owner.replace(marker, marker + marker, 1)
            duplicated_hash = hashlib.sha256(
                duplicated.encode("utf-8"),
            ).hexdigest()
            reject("reject-duplicated-actual-native-owner-marker-" + name,
                   lambda duplicated=duplicated,
                   duplicated_hash=duplicated_hash:
                   compose_guarded_owner(
                       duplicated, owner_source_sha256=duplicated_hash,
                   ))
        reject("reject-a-substituted-frozen-native-owner-worker-hash",
               lambda: compose_guarded_owner(
                   source_owner, owner_source_sha256="0" * 64,
               ))

        good_pins = {
            "v10_base_report": hashlib.sha256(b"source-only-v19-base").hexdigest(),
            "v10_strict_report": hashlib.sha256(
                b"source-only-v19-strict",
            ).hexdigest(),
            **{
                family + "_" + kind: hashlib.sha256(
                    ("source-only-v19:" + family + ":" + kind).encode("ascii"),
                ).hexdigest()
                for family in FAMILIES
                for kind in (
                    "edge_archive", "edge_proof", "deep_archive", "deep_proof",
                )
            },
        }
        check("require-all-fourteen-independent-original-v10-v11-pins",
              len(v18.proof_pin_values(good_pins)) == 14)
        for name in tuple(good_pins):
            missing = dict(good_pins)
            missing.pop(name)
            reject("reject-a-missing-original-owner-proof-pin-" + name,
                   lambda missing=missing: v18.proof_pin_values(missing))
            invalid = dict(good_pins)
            invalid[name] = "not-an-actual-sha256"
            reject("reject-a-forged-original-owner-proof-pin-" + name,
                   lambda invalid=invalid: v18.proof_pin_values(invalid))

        retry_pins = {
            family + "_deep_retry_proof": hashlib.sha256(
                ("source-only-v19-v12-retry:" + family).encode("ascii"),
            ).hexdigest()
            for family in FAMILIES
        }
        check("require-all-three-distinct-actual-v12-deep-retry-proof-pins",
              len(v12_retry_pin_values(retry_pins)) == 3)
        for name in tuple(retry_pins):
            missing = dict(retry_pins)
            missing.pop(name)
            reject("reject-missing-genuine-v12-retry-proof-pin-" + name,
                   lambda missing=missing: v12_retry_pin_values(missing))
            invalid = dict(retry_pins)
            invalid[name] = "not-an-actual-sha256"
            reject("reject-forged-genuine-v12-retry-proof-pin-" + name,
                   lambda invalid=invalid: v12_retry_pin_values(invalid))
        for family in FAMILIES:
            duplicate = dict(retry_pins)
            another = next(name for name in FAMILIES if name != family)
            duplicate[family + "_deep_retry_proof"] = duplicate[
                another + "_deep_retry_proof"
            ]
            reject("reject-reused-different-family-v12-retry-proof-" + family,
                   lambda duplicate=duplicate: v12_retry_pin_values(duplicate))
            check("pin-the-exact-genuine-v11-original-edge-archive-" + family,
                  V11_EDGE_ARCHIVE_RELATIVES[family]
                  == v18.V11_EDGE_ARCHIVE_RELATIVES[family])
            check("pin-the-exact-genuine-v11-durable-edge-owner-" + family,
                  V11_EDGE_PROOF_RELATIVES[family]
                  == v18.V11_EDGE_PROOF_RELATIVES[family])
            check("pin-the-exact-genuine-v11-original-deep-archive-" + family,
                  V11_DEEP_ARCHIVE_RELATIVES[family]
                  == v18.V11_DEEP_ARCHIVE_RELATIVES[family])
            check("pin-the-exact-genuine-v11-durable-deep-owner-" + family,
                  V11_DEEP_PROOF_RELATIVES[family]
                  == v18.V11_DEEP_PROOF_RELATIVES[family])
            check("pin-separate-genuine-v12-deep-retry-owner-" + family,
                  V12_DEEP_RETRY_PROOF_RELATIVES[family].endswith(
                      "-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json",
                  )
                  and V12_DEEP_RETRY_PROOF_RELATIVES[family]
                  != V11_DEEP_PROOF_RELATIVES[family])
        all_artifacts = [
            *V11_EDGE_ARCHIVE_RELATIVES.values(),
            *V11_EDGE_PROOF_RELATIVES.values(),
            *V11_DEEP_ARCHIVE_RELATIVES.values(),
            *V11_DEEP_PROOF_RELATIVES.values(),
            *V12_DEEP_RETRY_PROOF_RELATIVES.values(),
        ]
        check("require-all-fifteen-distinct-actual-original-and-retry-proofs",
              len(all_artifacts) == len(set(all_artifacts)) == 15)

        for family in FAMILIES:
            for deep_kind in (False, True):
                snapshot, wrapper, edge = v18._synthetic_durable_pair(
                    family, deep_kind, good_pins,
                )
                kind = "deep" if deep_kind else "edge"
                archive = (
                    V11_DEEP_ARCHIVE_RELATIVES[family]
                    if deep_kind else V11_EDGE_ARCHIVE_RELATIVES[family]
                )
                proof = (
                    V11_DEEP_PROOF_RELATIVES[family]
                    if deep_kind else V11_EDGE_PROOF_RELATIVES[family]
                )

                def validate_pair(
                    document: Any,
                    *,
                    family: str = family,
                    deep_kind: bool = deep_kind,
                    snapshot: Mapping[str, Any] = snapshot,
                    archive: str = archive,
                    proof: str = proof,
                    edge: Mapping[str, Any] = edge,
                ) -> Any:
                    return v18.validate_durable_pair_identity(
                        document,
                        family,
                        deep=deep_kind,
                        archive_relative=archive,
                        archive_sha256=good_pins[
                            family
                            + ("_deep_archive" if deep_kind else "_edge_archive")
                        ],
                        proof_relative=proof,
                        snapshot=snapshot,
                        v10_base_report_sha256=good_pins["v10_base_report"],
                        v10_strict_report_sha256=good_pins["v10_strict_report"],
                        qualified_edge=edge if deep_kind else None,
                    )

                check("retain-complete-immutable-v11-owner-shape-"
                      + family + "-" + kind,
                      validate_pair(wrapper) is wrapper)
                for field, wrong in (
                    ("status", "FAIL"),
                    ("campaign_qualified", False),
                    ("candidate_module", "candidates.other_candidate"),
                    ("proof_path", "candidates/audits/substituted.json"),
                    ("original_archive_path", "candidates/audits/wrong.json.gz"),
                    ("original_archive_sha256", "0" * 64),
                    ("original_archive_bytes", 0),
                    ("complete_original_producer_bytes_preserved", False),
                    ("original_archive_is_unmodified_original", False),
                    ("stdout_is_not_durable_proof", False),
                    ("original_worker_returncode", 1),
                    ("corrected_v10_native_owner_before", None),
                    ("corrected_v10_native_owner_after", None),
                    ("actual_v10_base_report_sha256", "0" * 64),
                    ("actual_v10_strict_report_sha256", "0" * 64),
                    ("exclusive_creation", False),
                    ("performance", "MEASURED"),
                    ("holdout", "ACCESSED"),
                ):
                    forged = copy.deepcopy(wrapper)
                    forged[field] = wrong
                    reject("reject-forged-immutable-v11-owner-"
                           + family + "-" + kind + "-" + field,
                           lambda forged=forged,
                           validate_pair=validate_pair: validate_pair(forged))
                if deep_kind:
                    forged = copy.deepcopy(wrapper)
                    forged["qualified_edge"]["proof_sha256"] = "0" * 64
                    reject("reject-a-deep-owner-without-its-real-edge-" + family,
                           lambda forged=forged,
                           validate_pair=validate_pair: validate_pair(forged))

        configuration = _synthetic_configuration()
        check("validate-the-exact-same-process-source-only-owner-context",
              verify_embedded_configuration(configuration) == configuration)
        for field in tuple(configuration):
            missing = dict(configuration)
            missing.pop(field)
            reject("reject-missing-live-owner-context-" + field,
                   lambda missing=missing:
                   verify_embedded_configuration(missing))
        for field, wrong in (
            ("schema", "substituted"),
            ("family", "foreign"),
            ("source_sha256", "not-a-sha256"),
            ("protocol_sha256", "not-a-sha256"),
            ("v17_source_sha256", "0" * 64),
            ("v17_protocol_sha256", "0" * 64),
            ("v18_source_sha256", "0" * 64),
            ("v18_protocol_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("stimulus_sha256", "0" * 64),
            ("cases", EXPECTED_CASES - 1),
            ("iso8859_1_locale", ""),
            ("utf8_locale", ""),
            ("expected_native_sha256", {}),
        ):
            forged = dict(configuration)
            forged[field] = wrong
            reject("reject-forged-live-owner-context-" + field,
                   lambda forged=forged:
                   verify_embedded_configuration(forged))
        same_locale = dict(configuration)
        same_locale["utf8_locale"] = same_locale["iso8859_1_locale"]
        reject("reject-identical-fake-iso8859-1-and-utf8-locales",
               lambda: verify_embedded_configuration(same_locale))

        for role in ("reference_a", "reference_b"):
            genuine_preflight = _synthetic_reference_failure(
                role, matrix, prefix_count=0, failure_stage="preflight",
            )
            check("preserve-a-genuine-no-row-reference-preflight-failure-" + role,
                  validate_reference_failure(
                      genuine_preflight,
                      role=role,
                      source_sha256="a" * 64,
                      protocol_sha256="b" * 64,
                  ) is genuine_preflight)
            genuine_postflight = _synthetic_reference_failure(
                role,
                matrix,
                prefix_count=EXPECTED_CASES,
                failure_stage="postflight",
            )
            check("preserve-all-1376-real-prefix-rows-on-postflight-failure-"
                  + role,
                  validate_reference_failure(
                      genuine_postflight,
                      role=role,
                      source_sha256="a" * 64,
                      protocol_sha256="b" * 64,
                  ) is genuine_postflight
                  and genuine_postflight["completed_count"] == EXPECTED_CASES
                  and genuine_postflight["active_case"] is None)
            for prefix in (0, 1, 14, 31):
                synthetic_failure = _synthetic_reference_failure(
                    role, matrix, prefix_count=prefix,
                )
                check("retain-real-inner-failure-prefix-" + role
                      + "-" + str(prefix),
                      validate_reference_failure(
                          synthetic_failure,
                          role=role,
                          source_sha256="a" * 64,
                          protocol_sha256="b" * 64,
                      ) is synthetic_failure)
            actual_failure = _synthetic_reference_failure(
                role, matrix, prefix_count=14,
            )

            def validate_failure(
                document: Any,
                *,
                role: str = role,
            ) -> Any:
                return validate_reference_failure(
                    document,
                    role=role,
                    source_sha256="a" * 64,
                    protocol_sha256="b" * 64,
                )

            for field, wrong in (
                ("schema", "forged"),
                ("status", "PASS"),
                ("role", "substituted"),
                ("python", "3.13.0"),
                ("source_sha256", "0" * 64),
                ("protocol_sha256", "0" * 64),
                ("v17_source_sha256", "0" * 64),
                ("v17_protocol_sha256", "0" * 64),
                ("v18_source_sha256", "0" * 64),
                ("v18_protocol_sha256", "0" * 64),
                ("matrix_sha256", "0" * 64),
                ("stimulus_sha256", "0" * 64),
                ("expected_cases", EXPECTED_CASES - 1),
                ("completed_count", 13),
                ("active_case", "surface16.99.99"),
                ("requested_locales", {}),
                ("actual_error", None),
                ("traceback", ""),
                ("candidate_audits_read", 1),
                ("candidate_proofs_read", 1),
                ("v12_sources_read", 1),
                ("current_graph_candidate_qualification", "PASS"),
                ("candidate_evidence_current", "QUALIFIED"),
                ("holdout_cases_read", 1),
                ("performance_fixtures_read", 1),
                ("benchmark_or_timing_executed", True),
                ("performance", "MEASURED"),
            ):
                forged = copy.deepcopy(actual_failure)
                forged[field] = wrong
                reject("reject-forged-full-inner-reference-failure-"
                       + role + "-" + field,
                       lambda forged=forged,
                       validate_failure=validate_failure:
                       validate_failure(forged))
            for field in (
                "current_graph_candidate_qualification",
                "candidate_evidence_current",
                "current_graph_candidate_qualification_reason",
            ):
                omitted = copy.deepcopy(actual_failure)
                omitted.pop(field)
                reject("reject-omitted-reference-candidate-block-"
                       + role + "-" + field,
                       lambda omitted=omitted,
                       validate_failure=validate_failure:
                       validate_failure(omitted))
                forged_true = copy.deepcopy(actual_failure)
                forged_true[field] = True
                reject("reject-boolean-reference-candidate-qualification-"
                       + role + "-" + field,
                       lambda forged_true=forged_true,
                       validate_failure=validate_failure:
                       validate_failure(forged_true))
            no_active = copy.deepcopy(actual_failure)
            no_active["active_case"] = None
            reject("reject-the-actual-v18-lost-active-case-regression-" + role,
                   lambda no_active=no_active,
                   validate_failure=validate_failure:
                   validate_failure(no_active))
            no_stage = copy.deepcopy(actual_failure)
            no_stage.pop("failure_stage")
            reject("reject-a-missing-actual-reference-failure-stage-" + role,
                   lambda no_stage=no_stage,
                   validate_failure=validate_failure:
                   validate_failure(no_stage))
            for wrong_stage in ("preflight", "postflight", "concealed"):
                substituted_stage = copy.deepcopy(actual_failure)
                substituted_stage["failure_stage"] = wrong_stage
                reject("reject-a-substituted-reference-failure-stage-"
                       + role + "-" + wrong_stage,
                       lambda substituted_stage=substituted_stage,
                       validate_failure=validate_failure:
                       validate_failure(substituted_stage))
            forged_prefix = copy.deepcopy(actual_failure)
            forged_prefix["completed_records"][0]["id"] = "surface16.99.99"
            reject("reject-swapped-actual-failure-prefix-" + role,
                   lambda forged_prefix=forged_prefix,
                   validate_failure=validate_failure:
                   validate_failure(forged_prefix))
            candidate_guard = copy.deepcopy(actual_failure)
            candidate_guard["guard"]["candidate_imported"] = True
            reject("reject-candidate-inside-actual-python-reference-" + role,
                   lambda candidate_guard=candidate_guard,
                   validate_failure=validate_failure:
                   validate_failure(candidate_guard))

        expected_raise_row = matrix[0]
        expected_raise = {
            "id": expected_raise_row["id"],
            "cohort": expected_raise_row["cohort"],
            "stimulus_sha256": digest(v17.build_stimulus(expected_raise_row)),
            "outcome": {
                "status": "raise",
                "exception": normalize(_source_error()),
            },
        }
        check("retain-a-real-seeded-python-exception-as-an-observation",
              validate_partial_records([expected_raise], matrix)
              ["additional_cases"] == 0)
        first_additional = next(
            index
            for index, row in enumerate(matrix)
            if row["cohort"] in v17.ADDITIONAL_COHORTS
            and row["cohort"] not in {
                "real-locale-switch-on-compiled-bytes",
                "real-locale-invalid-flags-and-cache",
            }
        )
        additional_records = _synthetic_reference_failure(
            "reference_a", matrix, prefix_count=first_additional + 1,
        )["completed_records"]
        additional_records[-1]["outcome"] = {
            "status": "raise",
            "exception": normalize(_source_error()),
        }
        additional_counts = validate_partial_records(additional_records, matrix)
        check("retain-an-expected-seeded-extended-public-exception",
              additional_counts["additional_cases"] >= 1
              and additional_counts["raised_additional_cases"] >= 1)

        for role in ("reference_a", "reference_b", *FAMILIES):
            document = {
                "schema": "source-only-v19-complete-worker-stream",
                "role": role,
                "status": "PASS",
            }
            stdout = canonical(document) + b"\n"
            process = {
                "role": role,
                "returncode": 0,
                "stdout": capture_complete_stream(stdout),
                "stderr": capture_complete_stream(b""),
            }
            check("retain-the-complete-original-source-only-stream-" + role,
                  validate_process_streams(
                      process, role=role, expected_document=document,
                  ) is process)
            for field, wrong in (
                ("role", "substituted-worker"),
                ("returncode", 1),
            ):
                forged = copy.deepcopy(process)
                forged[field] = wrong
                reject("reject-changed-original-worker-" + role + "-" + field,
                       lambda forged=forged, role=role, document=document:
                       validate_process_streams(
                           forged, role=role, expected_document=document,
                       ))
            for label, wrong in (
                ("false", False),
                ("true", True),
                ("none", None),
                ("negative", -1),
            ):
                forged = copy.deepcopy(process)
                forged["returncode"] = wrong
                reject("reject-forged-exact-worker-exit-type-"
                       + role + "-" + label,
                       lambda forged=forged, role=role, document=document:
                       validate_process_streams(
                           forged, role=role, expected_document=document,
                       ))
            for field, wrong in (
                ("bytes", 0),
                ("sha256", "0" * 64),
                ("complete", False),
                ("base64", "not original base64!"),
            ):
                forged = copy.deepcopy(process)
                forged["stdout"][field] = wrong
                reject("reject-hidden-original-worker-stdout-"
                       + role + "-" + field,
                       lambda forged=forged, role=role, document=document:
                       validate_process_streams(
                           forged, role=role, expected_document=document,
                       ))
            concealed = copy.deepcopy(process)
            concealed["stderr"] = capture_complete_stream(
                b"actual concealed worker failure",
            )
            reject("reject-concealed-actual-worker-stderr-" + role,
                   lambda concealed=concealed, role=role, document=document:
                   validate_process_streams(
                       concealed, role=role, expected_document=document,
                   ))
            actual_timeout = subprocess.TimeoutExpired(
                ["source-only-v19-worker", role],
                7,
                output=("source-only-incomplete-stdout:" + role).encode("ascii"),
                stderr=("source-only-incomplete-stderr:" + role).encode("ascii"),
            )
            retained_timeout = _timeout_failure_details(role, actual_timeout)
            check("retain-genuine-incomplete-timeout-child-stdout-" + role,
                  retained_timeout["timed_out"] is True
                  and retained_timeout["returncode"] is None
                  and retained_timeout["timeout_seconds"] == 7
                  and retained_timeout["stdout"]["complete"] is False
                  and retained_timeout["stdout"]["captured_before_timeout"]
                  is True
                  and retained_timeout["stdout"]["sha256"]
                  == hashlib.sha256(actual_timeout.stdout).hexdigest())
            check("retain-genuine-incomplete-timeout-child-stderr-" + role,
                  retained_timeout["stderr"]["complete"] is False
                  and retained_timeout["stderr"]["captured_before_timeout"]
                  is True
                  and retained_timeout["stderr"]["sha256"]
                  == hashlib.sha256(actual_timeout.stderr).hexdigest())
            reject("never-qualify-incomplete-timeout-stdout-" + role,
                   lambda retained_timeout=retained_timeout:
                   restore_complete_stream(
                       retained_timeout["stdout"],
                       label="source-only incomplete timeout stdout",
                   ))
            reject("never-qualify-incomplete-timeout-stderr-" + role,
                   lambda retained_timeout=retained_timeout:
                   restore_complete_stream(
                       retained_timeout["stderr"],
                       label="source-only incomplete timeout stderr",
                   ))

        for label, value in (
            ("absolute", "/tmp/forged-v19.json"),
            ("parent", "../forged-v19.json"),
            ("nested-parent", "candidates/../forged-v19.json"),
            ("backslash", "candidates\\forged-v19.json"),
            ("nul", "candidates/forged\x00-v19.json"),
            ("unapproved", "candidates/evidence/unapproved-v19.json"),
            ("frozen-v18-failure", V18_HISTORICAL_FAILURE_RELATIVE),
        ):
            reject("reject-dangerous-or-historical-exclusive-output-" + label,
                   lambda value=value: safe_relative(value, outputs_only=True))
        for relative in sorted(APPROVED_OUTPUTS):
            check("allow-only-new-v19-exclusive-output-"
                  + relative.rsplit("/", 1)[-1],
                  safe_relative(relative, outputs_only=True) == relative)

        for label, counter in (
            ("read-zero-candidates-evidence-proofs-v12-fixtures-and-holdouts",
             "files_read"),
            ("write-zero-reports-bytecode-evidence-or-other-files",
             "files_written"),
            ("start-zero-reference-native-candidate-or-proof-workers",
             "processes"),
            ("start-zero-threads-or-background-oracles", "threads"),
            ("sample-zero-wall-performance-or-correctness-clocks",
             "clock_samples"),
            ("draw-zero-production-randomness", "entropy_draws"),
            ("change-zero-global-locales", "locale_changes"),
            ("import-zero-candidate-or-external-regex-implementations",
             "candidate_imports"),
            ("execute-zero-standard-library-regular-expression-matches",
             "regex_matches"),
        ):
            check(label, effects[counter] == 0)

    failures = [row["name"] for row in checks if row["passed"] is not True]
    require(not failures,
            "a genuine V19 candidate-free poison failed: "
            + ", ".join(failures))
    require(len(checks) >= 800,
            "at least 800 distinct actual V19 source-only checks are required")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "protocol_path": PROTOCOL_RELATIVE,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v18_source_sha256": V18_SOURCE_SHA256,
        "v18_protocol_sha256": V18_PROTOCOL_SHA256,
        "v12_source_sha256": V12_SOURCE_SHA256,
        "v12_protocol_sha256": V12_PROTOCOL_SHA256,
        "historical_v18_failure_path": V18_HISTORICAL_FAILURE_RELATIVE,
        "historical_v18_failure_sha256": V18_HISTORICAL_FAILURE_SHA256,
        "historical_failure_qualifies_current_build": False,
        "current_graph_candidate_qualification":
            CURRENT_GRAPH_CANDIDATE_QUALIFICATION,
        "candidate_evidence_current": CURRENT_GRAPH_CANDIDATE_EVIDENCE,
        "current_graph_candidate_qualification_reason":
            CURRENT_GRAPH_CANDIDATE_QUALIFICATION_REASON,
        "historical_candidate_helpers_executed": False,
        "check_count": len(checks),
        "inherited_v18_check_count": inherited["check_count"],
        "inherited_v17_check_count": inherited["inherited_v17_check_count"],
        "total_independent_source_controls": (
            len(checks) + inherited["total_independent_source_controls"]
        ),
        "failed": [],
        "cohorts": EXPECTED_COHORTS,
        "cases": EXPECTED_CASES,
        "source_local_base_cases": inherited["source_local_base_cases"],
        "additional_cases": EXPECTED_ADDITIONAL_CASES,
        "distinct_behavioral_stimuli": EXPECTED_CASES,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "public_exports": len(v17.PUBLIC_EXPORTS),
        "public_pattern_members": len(v17.PUBLIC_PATTERN_MEMBERS),
        "public_match_members": len(v17.PUBLIC_MATCH_MEMBERS),
        "required_v11_qualified_original_archives": 6,
        "required_v11_complete_durable_owner_proofs": 6,
        "required_v12_complete_deep_retry_owner_proofs": 3,
        "declared_immutable_instruction_files_read": 4,
        "v12_source_files_read": 0,
        "candidate_source_files_read": effects["files_read"],
        "evidence_files_read": effects["files_read"],
        "files_written": effects["files_written"],
        "candidate_imports": effects["candidate_imports"],
        "subprocesses": effects["processes"],
        "threads_started": effects["threads"],
        "clock_samples": effects["clock_samples"],
        "entropy_draws": effects["entropy_draws"],
        "locale_changes": effects["locale_changes"],
        "regex_matching_calls": effects["regex_matches"],
        "reference_oracle_executed": False,
        "candidate_oracle_executed": False,
        "report_written": False,
        "subinterpreter_coverage": "NOT RUN",
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all",))
    modes.add_argument("--reference-worker", choices=("reference_a", "reference_b"),
                       help=argparse.SUPPRESS)
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--reference-sha256")
    parser.add_argument("--iso8859-1-locale", dest="iso8859_1_locale")
    parser.add_argument("--utf8-locale")
    parser.add_argument("--v10-base-report-sha256")
    parser.add_argument("--v10-strict-report-sha256")
    for family in FAMILIES:
        for kind in (
            "edge-archive", "edge-proof", "deep-archive", "deep-proof",
            "deep-retry-proof",
        ):
            parser.add_argument("--" + family + "-" + kind + "-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            document = self_test()
        elif options.reference_worker:
            document = _reference_worker_document(
                options.reference_worker,
                options.source_sha256,
                options.protocol_sha256,
                _locale_names(options),
            )
        elif options.self_oracle:
            document = run_self_oracle(options)
        else:
            document = run_all_candidates(options)
        sys.stdout.write(canonical(document).decode("ascii") + "\n")
        return 0 if document.get("status") == "PASS" else 1
    except (
        PublicSurfaceV19Error,
        v17.PublicSurfaceError,
        v18.PublicSurfaceV18Error,
        AssertionError,
        OSError,
        subprocess.SubprocessError,
        ValueError,
        TypeError,
        KeyError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        sys.stderr.write(canonical({
            "schema": SCHEMA,
            "status": "FAIL",
            **_error_details(error),
            "performance": "NOT MEASURED",
        }).decode("ascii") + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
