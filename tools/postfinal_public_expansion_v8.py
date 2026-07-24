#!/usr/bin/env python3
"""Prepare, but never implicitly run, the enlarged public-development suite.

All real input is public.  ``--self-test`` uses synthetic, in-memory data only;
it neither opens the public fixtures nor runs an oracle, candidate, or timer.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
PINNED_PYTHON = Path("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14")
SEED_DOMAIN = "rebar/public-development/v8"
SELECTION_SEED = 2_026_072_428
ORDER_SEED = 2_026_072_429
BOOTSTRAP_SEED = 2_026_072_430
ORDER_SEED_DOMAIN = f"{SEED_DOMAIN}/paired-order"
BOOTSTRAP_SEED_DOMAIN = f"{SEED_DOMAIN}/bootstrap"
CATEGORY_COUNT = 260
CASES_PER_CATEGORY = 128
CASE_COUNT = CATEGORY_COUNT * CASES_PER_CATEGORY
ORIGINAL_CASE_COUNT = 8_192
FIXTURE_CASE_COUNT = 10_312
WARMUPS = 4
PAIRED_TRIALS = 13
BOOTSTRAP_DRAWS = 2_000
SUBJECT_LIMIT = 8_192
RESULT_LIMIT = 128
MAX_PROGRAM_SOURCE_BYTES = 4 * 1024 * 1024
MAX_PROTOCOL_BYTES = 256 * 1024
MAX_OWNED_ARTIFACT_BYTES = 64 * 1024 * 1024
BASELINE = "re"
CANDIDATES = ("candidates.rust_candidate", "candidates.vm_candidate", "candidates.zig_candidate")
REQUIRED_FAMILIES = frozenset({"rust", "vm", "zig"})
REQUIRED_NATIVE_ROLES = frozenset({
    "candidates.rust_candidate:native-bridge",
    "candidates.rust_candidate:native-engine",
    "candidates.vm_candidate:native-engine",
    "candidates.zig_candidate:native-bridge",
    "candidates.zig_candidate:native-engine",
})
REQUIRED_NATIVE_FILES = {
    "candidates.rust_candidate:native-bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    "candidates.rust_candidate:native-engine": "candidates/_rust_engine.so",
    "candidates.vm_candidate:native-engine": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "candidates.zig_candidate:native-bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    "candidates.zig_candidate:native-engine": "candidates/_zig_probe.so",
}
NATIVE_RECORD_ROLES = {
    "rust": {"bridge": "candidates.rust_candidate:native-bridge",
             "engine": "candidates.rust_candidate:native-engine"},
    "vm": {"native": "candidates.vm_candidate:native-engine"},
    "zig": {"bridge": "candidates.zig_candidate:native-bridge",
            "engine": "candidates.zig_candidate:native-engine"},
}
REQUIRED_SOURCE_PATHS = frozenset({
    "candidates/_vm_native.c",
    "candidates/rust/py_bridge.c",
    "candidates/rust/src/lib.rs",
    "candidates/rust/src/newline.rs",
    "candidates/rust/src/search.rs",
    "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs",
    "candidates/rust_candidate.py",
    "candidates/vm_candidate.py",
    "candidates/zig/mini_regex.zig",
    "candidates/zig/py_bridge.c",
    "candidates/zig_candidate.py",
})
PUBLIC_OPERATIONS = (
    "compile", "escape", "findall", "finditer", "fullmatch", "match",
    "match-surface", "scanner", "search", "split", "sub", "subn",
)
SCHEMA = "rebar-postfinal-public-development-plan-v8"
FIXTURE_SCHEMA = "rebar-rust-sealed-calibration-fixture-v7"
FIXTURE_MANIFEST_SCHEMA = "rebar-rust-sealed-calibration-fixture-manifest-v7"
ORACLE_SCHEMA = "rebar-postfinal-public-development-self-oracle-v8"
UNIVERSAL_CASE_SHA256 = "8e5c120a4e637c30940363e20d6042324d65d9f7d03fbd35240ffabf2df282ae"
STAGE10_SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage10.py"
STAGE10_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md"
STAGE10_SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json"
)
STAGE10_ALL_CANDIDATES_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v10-all.json"
)
STAGE10_SELF_ORACLE_SCHEMA = "rebar-python-re-public-contract-v10-self-oracle"
STAGE10_ALL_CANDIDATES_SCHEMA = "rebar-python-re-public-contract-v10-all-candidates"
STAGE10_METADATA_SCHEMA = (
    "rebar-python-re-public-contract-v10-isolated-public-metadata"
)
STAGE10_OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v10"
STAGE10_NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)
STAGE10_SEED = 2_026_072_437
STAGE10_SEED_DOMAIN = "rebar/python-re/public-contract/v7"
STAGE10_MATRIX_SHA256 = (
    "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
)
STAGE10_CASES = 3_584
STAGE10_COHORTS = 8
STAGE10_COHORT_CASES = {
    "public-surface": 256,
    "invalid-grammar": 256,
    "real-locale": 1_024,
    "buffer-lifetime": 256,
    "object-contract": 256,
    "callback-scanner": 256,
    "shared-pattern-threads": 256,
    "bounded-unicode": 1_024,
}
# Bind only the root-confirmed, pushed producer, protocol, and two genuinely
# passing public reports. A missing, stale, or changed hash fails closed before
# public fixture generation or an independent V8 CPython worker.
STAGE10_PINNED_SHA256: dict[str, str | None] = {
    STAGE10_SOURCE_RELATIVE:
        "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08",
    STAGE10_PROTOCOL_RELATIVE:
        "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543",
    STAGE10_SELF_ORACLE_RELATIVE:
        "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9",
    STAGE10_ALL_CANDIDATES_RELATIVE:
        "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7",
}
PACKING_MARKER = "__rebar_calibration_type__"
PUBLIC_FILE_SHA256: dict[str, str] = {
    "GOAL.md": "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "performance/postfinal-public-v6/manifest.json": "65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a",
    "performance/v7/evidence/rust-calibration-fixture-manifest.json": "2ff780cd43ab4948a2af2f37e3d5dd3bbb69b9dd924385de1f2f3fc924dd276a",
    "performance/v7/evidence/rust-calibration-fixture.jsonl.gz": "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5",
    "tools/rust_v7_calibration_pilot.py": "d7dc76bb439f8e8abbee79bcfd0a09c3aabf72db47c9d259bdf12704829f5890",
    "tools/postfinal_public_practice_v3.py": "aa2b22de82894dc41622378d1bd782636358fa360454be37f3b8fedbc6e4989a",
    "tools/postfinal_public_practice_v4.py": "69d42bf668b60145520ac54873966ccf52c42d624bab809e484e239229256600",
    "tools/postfinal_public_practice_v6.py": "16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3",
    "performance/postfinal-public-v6/PROTOCOL.md": "166f9c65eae008426c2d84e64240f6ddf667412d047f643726b7a377337e52c2",
    "tools/postfinal_public_practice_v7.py": "cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e",
    "performance/postfinal-public-v7/PROTOCOL.md": "c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0",
    "tools/postfinal_from_scratch_audit_v5.py": "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843",
    "tools/postfinal_no_delegation_audit_v5.py": "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6",
    "tools/postfinal_no_delegation_audit_v1.py": "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed",
    "tools/postfinal_cpython_locale_oracle_v1.py": "b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55",
    "tools/python_re_universal_public_oracle_stage06.py": "ff365f1d867f4873146aaf6f77fa2f360b197bbccfb9dd06239bdcf4b776e7f2",
    "tools/python_re_universal_public_oracle_stage07.py": "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25",
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md": "b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524",
    "oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json": "765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0",
    "tools/python_re_universal_public_oracle_stage08.py": "10464ca347e6eab248a2887a6fd0625cff63497173024616ca8338af0801b0aa",
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md": "502f300e8ffbd33cf3cbbf6fde7e9cb5e81ed3f87f83634f47068015cdd9dbdd",
    "oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle.json": "efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df",
    "candidates/evidence/python-re-universal-public-oracle-v8-rust-failures.json": "f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1",
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json": "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198",
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json": "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb",
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json": "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621",
    "candidates/evidence/python-re-universal-public-oracle-v6-all.json": "bf4f7cc82c876ee54e55c0971c65db209f6fdf0c8b00baa8c57fbc5f460b1528",
    "candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v1.json.gz": "8569275c5b705870bde368ee20981be1a90c07675b12fe53b64f19c7e765b408",
    "candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v1.json.gz": "0c07fdbf8848f4236735c97bbda4969c4de0ceb6e10c11fdac0c674d5efd303b",
    "candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v1.json.gz": "8a8f76a85e2888dc0eb19e07c7343dd5c8caeab8745baf8a277f68beea1424a6",
    "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-LOCALE-V1.json.gz": "ca437ae8e2dc46f4d0b8e259f304a402efc6f0817dfe89600d92728a86c2ce9f",
    "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-LOCALE-V1.json.gz": "9d8aa10cd07d4bee48b021f26fbb66e5d2f3293f6c1d8a0d1039a9087af932de",
    "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-LOCALE-V1.json.gz": "f522ae69bea26792b8406254360809ae9cfddeb03cc012dc579f2397c7e8813d",
    "candidates/evidence/rust-v8-observability-rust-qualified-postfinal-locale-v1.json.gz": "db139cf63dfe6605120a9e36db16b749f060fc31961fe6215397623b454929fa",
    "candidates/evidence/rust-v8-observability-vm-qualified-postfinal-locale-v1.json.gz": "35c63238162f420c41a5b021641530344d91ddc036b15dac73705b3f144ee43b",
    "candidates/evidence/rust-v8-observability-zig-qualified-postfinal-locale-v1.json.gz": "43053dd764ee9b6c40ccfee72107b1e1ebe56e1081b951ec026c3ab8c124e15d",
}


class PublicExpansionError(RuntimeError):
    """A public provenance, semantic, uniqueness, or oracle gate failed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise PublicExpansionError(message)


def json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def seed_key(label: str, *, domain: str = SEED_DOMAIN, seed: int = SELECTION_SEED) -> tuple[bytes, str]:
    require(isinstance(label, str) and bool(label), "empty public selection label")
    require(isinstance(domain, str) and bool(domain), "missing public seed domain")
    require(isinstance(seed, int) and not isinstance(seed, bool), "invalid public selection seed")
    material = json_bytes([domain, seed, label])
    return hashlib.sha256(material).digest(), label


def canonical(value: Any) -> Any:
    """Tag every source type, including bytes and lone-surrogate strings."""
    if value is None:
        return ["none"]
    if isinstance(value, bool):
        return ["bool", value]
    if isinstance(value, int):
        return ["int", str(value)]
    if isinstance(value, str):
        return ["text", value.encode("utf-8", "surrogatepass").hex()]
    if isinstance(value, bytes):
        return ["bytes", value.hex()]
    if isinstance(value, bytearray):
        return ["bytearray", bytes(value).hex()]
    if isinstance(value, memoryview):
        return ["memoryview", bytes(value).hex(), value.format, value.readonly]
    if isinstance(value, tuple):
        return ["tuple", [canonical(item) for item in value]]
    if isinstance(value, list):
        return ["list", [canonical(item) for item in value]]
    if isinstance(value, dict):
        marker = value.get(PACKING_MARKER)
        if marker in {"bytes", "bytearray", "memoryview"}:
            require(set(value) == {PACKING_MARKER, "hex"}, "invalid tagged public buffer")
            encoded = value["hex"]
            require(isinstance(encoded, str), "invalid tagged public buffer payload")
            try:
                payload = bytes.fromhex(encoded)
            except ValueError as error:
                raise PublicExpansionError("invalid tagged public buffer hexadecimal") from error
            return [marker, payload.hex()]
        if marker == "tuple":
            require(set(value) == {PACKING_MARKER, "items"}, "invalid tagged public tuple")
            require(isinstance(value["items"], list), "invalid tagged public tuple payload")
            return ["tuple", [canonical(item) for item in value["items"]]]
        require(marker is None, "unknown or reserved public serialization marker")
        pairs = [(canonical(key), canonical(item)) for key, item in value.items()]
        return ["dict", sorted(pairs, key=lambda pair: json_bytes(pair[0]))]
    raise PublicExpansionError(f"unsupported canonical public value: {type(value).__name__}")


NON_SEMANTIC_CASE_KEYS = frozenset({
    "api", "pattern", "flags", "string", "lifecycle", "id", "category",
    "cohort", "ops", "weight",
})


def semantic_identity(case: dict[str, Any]) -> str:
    require(isinstance(case, dict), "public semantic identity is not an object")
    required = ("api", "pattern", "flags", "string", "lifecycle")
    require(all(key in case for key in required), "incomplete public semantic identity")
    arguments = {key: value for key, value in case.items() if key not in NON_SEMANTIC_CASE_KEYS}
    return digest([
        canonical(case["api"]), canonical(case["pattern"]),
        canonical(case["flags"]), canonical(case["string"]),
        canonical(case["lifecycle"]), canonical(arguments),
    ])


def unpack(value: Any) -> Any:
    if isinstance(value, list):
        return [unpack(item) for item in value]
    if not isinstance(value, dict):
        return value
    marker = value.get(PACKING_MARKER)
    if marker is None:
        return {key: unpack(item) for key, item in value.items()}
    if marker in {"bytes", "bytearray", "memoryview"}:
        require(set(value) == {PACKING_MARKER, "hex"}, "invalid public byte representation")
        try:
            payload = bytes.fromhex(value["hex"])
        except (TypeError, ValueError) as error:
            raise PublicExpansionError("invalid public byte representation") from error
        return {"bytes": bytes, "bytearray": bytearray, "memoryview": memoryview}[marker](payload)
    if marker == "tuple":
        require(set(value) == {PACKING_MARKER, "items"}, "invalid public tuple representation")
        require(isinstance(value["items"], list), "invalid public tuple representation")
        return tuple(unpack(item) for item in value["items"])
    raise PublicExpansionError("unknown public calibration serialization marker")


def snapshot(value: Any) -> Any:
    """Use the exact public fixture's JSON representation, not an approximation."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"bytes_hex": bytes(value).hex()}
    if isinstance(value, tuple):
        return [snapshot(item) for item in value]
    if isinstance(value, list):
        return [snapshot(item) for item in value]
    if isinstance(value, dict):
        return {key: snapshot(item) for key, item in value.items()}
    return value


def skip_json_value(source: str, offset: int) -> int:
    """Skip an opaque JSON value without constructing or inspecting its content."""
    size = len(source)
    while offset < size and source[offset] in " \t\r\n":
        offset += 1
    require(offset < size, "truncated opaque public fixture field")
    first = source[offset]
    if first == '"':
        cursor = offset + 1
        while cursor < size:
            character = source[cursor]
            if character == "\\":
                cursor += 2
            elif character == '"':
                return cursor + 1
            else:
                cursor += 1
        raise PublicExpansionError("unterminated opaque public fixture string")
    if first in "[{":
        stack = ["]" if first == "[" else "}"]
        cursor = offset + 1
        quoted = False
        while cursor < size and stack:
            character = source[cursor]
            if quoted:
                if character == "\\":
                    cursor += 2
                    continue
                if character == '"':
                    quoted = False
            elif character == '"':
                quoted = True
            elif character in "[{":
                stack.append("]" if character == "[" else "}")
            elif character in "]}":
                require(character == stack.pop(), "mismatched opaque public fixture brackets")
            cursor += 1
        require(not stack and not quoted, "truncated opaque public fixture field")
        return cursor
    cursor = offset
    while cursor < size and source[cursor] not in ",}] \t\r\n":
        cursor += 1
    require(cursor > offset, "invalid opaque public fixture value")
    return cursor


def decode_public_fixture_line(raw: bytes, decoder: Any = None) -> dict[str, Any]:
    """Decode only public case/answer fields; leave archive history opaque."""
    require(isinstance(raw, bytes), "public fixture line is not opaque bytes")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise PublicExpansionError("public fixture line is not valid UTF-8") from error
    parser = json.JSONDecoder() if decoder is None else decoder
    offset = 0

    def whitespace(position: int) -> int:
        while position < len(source) and source[position] in " \t\r\n":
            position += 1
        return position

    offset = whitespace(offset)
    require(offset < len(source) and source[offset] == "{", "public fixture row is not an object")
    offset += 1
    result: dict[str, Any] = {}
    observed_keys: set[str] = set()
    public_keys = frozenset({"schema", "cohort", "position", "case", "expected"})
    opaque_key = "historical"
    while True:
        offset = whitespace(offset)
        require(offset < len(source), "truncated public fixture row")
        if source[offset] == "}":
            offset += 1
            break
        try:
            key, offset = parser.raw_decode(source, offset)
        except (ValueError, UnicodeError) as error:
            raise PublicExpansionError("invalid public fixture field name") from error
        require(isinstance(key, str), "non-string public fixture field name")
        require(key in public_keys or key == opaque_key, "unexpected public fixture field")
        require(key not in observed_keys, "duplicate public fixture field")
        observed_keys.add(key)
        offset = whitespace(offset)
        require(offset < len(source) and source[offset] == ":", "missing public fixture field separator")
        offset = whitespace(offset + 1)
        if key == opaque_key:
            offset = skip_json_value(source, offset)
        else:
            try:
                value, offset = parser.raw_decode(source, offset)
            except (ValueError, UnicodeError) as error:
                raise PublicExpansionError("invalid public fixture field") from error
            result[key] = value
        offset = whitespace(offset)
        require(offset < len(source), "truncated public fixture row separator")
        if source[offset] == "}":
            offset += 1
            break
        require(source[offset] == ",", "invalid public fixture row separator")
        offset += 1
    require(whitespace(offset) == len(source), "trailing public fixture row content")
    require(set(result) == public_keys, "incomplete public fixture record")
    return result


def source_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def bounded_source_file_sha256(path: Path, limit: int, label: str) -> str:
    require(isinstance(path, Path), f"invalid {label} path")
    require(isinstance(limit, int) and not isinstance(limit, bool) and limit > 0,
            f"invalid {label} size bound")
    require(not path.is_symlink(), f"symbolic-link {label} is forbidden")
    try:
        information = path.stat()
    except OSError as error:
        raise PublicExpansionError(f"missing {label}") from error
    require(path.is_file(), f"{label} is not a regular file")
    require(0 < information.st_size <= limit, f"{label} exceeds its size bound")
    hasher = hashlib.sha256()
    observed = 0
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(min(1024 * 1024, limit + 1)), b""):
                observed += len(block)
                require(observed <= limit, f"{label} grew past its size bound")
                hasher.update(block)
    except OSError as error:
        raise PublicExpansionError(f"cannot read {label}") from error
    require(observed == information.st_size, f"{label} changed during bounded hashing")
    return hasher.hexdigest()


def public_program_fingerprints() -> dict[str, str]:
    """Dynamically bind this exact source and protocol; never self-hard-code."""
    runner_relative = "tools/postfinal_public_expansion_v8.py"
    protocol_relative = "performance/postfinal-public-v8/PROTOCOL.md"
    runner = ROOT / runner_relative
    protocol = ROOT / protocol_relative
    require(Path(__file__).resolve() == runner.resolve(),
            "public V8 generator was not started from its exact owned path")
    require(not runner.is_symlink() and not protocol.is_symlink(),
            "public V8 source/protocol symbolic links are forbidden")
    require(runner.resolve().parent == (ROOT / "tools").resolve(),
            "public V8 runner escaped its approved source root")
    require(protocol.resolve().parent == (ROOT / "performance/postfinal-public-v8").resolve(),
            "public V8 protocol escaped its approved source root")
    return {
        "runner_path": runner_relative,
        "runner_sha256": bounded_source_file_sha256(
            runner, MAX_PROGRAM_SOURCE_BYTES, "public V8 generator source"),
        "protocol_path": protocol_relative,
        "protocol_sha256": bounded_source_file_sha256(
            protocol, MAX_PROTOCOL_BYTES, "public V8 protocol"),
    }


def read_pinned_json(relative: str) -> dict[str, Any]:
    require(relative in PUBLIC_FILE_SHA256, "unapproved public input")
    path = ROOT / relative
    require(path.is_file(), f"missing pinned public input: {relative}")
    require(source_file_sha256(path) == PUBLIC_FILE_SHA256[relative], f"changed pinned public input: {relative}")
    try:
        document = json.loads(path.read_bytes())
    except (OSError, UnicodeError, ValueError) as error:
        raise PublicExpansionError(f"cannot decode pinned public input: {relative}") from error
    require(isinstance(document, dict), f"pinned public input is not an object: {relative}")
    return document


def validate_public_source_documents(parent: dict[str, Any], fixture: dict[str, Any]) -> None:
    """Validate public manifest objects without opening any files."""
    require(isinstance(parent, dict), "original public plan is not an object")
    require(isinstance(fixture, dict), "sealed public fixture manifest is not an object")
    require(parent.get("postfinal_schema") == "rebar-postfinal-public-practice-plan-v6", "changed original public plan")
    require(parent.get("python") == "3.14.6", "changed original public Python")
    require(parent.get("cases") == ORIGINAL_CASE_COUNT, "changed original public denominator")
    require(parent.get("cohort") == "calibration", "original plan is not public calibration")
    require(parent.get("all_bounded_workload_categories") == CATEGORY_COUNT, "changed original public categories")
    operations = parent.get("public_operations", {})
    require(isinstance(operations, dict), "original public operation counts are not an object")
    require(set(operations) == set(PUBLIC_OPERATIONS), "changed original public operations")
    require(all(isinstance(count, int) and not isinstance(count, bool) and count > 0
                for count in operations.values()), "invalid original public operation denominator")
    require(sum(operations.values()) == ORIGINAL_CASE_COUNT, "changed original public operation denominator")
    categories = parent.get("categories", {})
    require(isinstance(categories, dict) and len(categories) == CATEGORY_COUNT,
            "changed original public category map")
    require(all(isinstance(count, int) and not isinstance(count, bool)
                and 0 < count <= CASES_PER_CATEGORY for count in categories.values()),
            "invalid original public category allocation")
    require(sum(categories.values()) == ORIGINAL_CASE_COUNT,
            "changed original public category denominator")
    require(fixture.get("schema") == FIXTURE_MANIFEST_SCHEMA, "changed sealed public fixture schema")
    require(fixture.get("python") == "3.14.6", "changed sealed public fixture Python")
    require(fixture.get("cohort") == "calibration", "fixture is not exclusively public calibration")
    require(fixture.get("cases") == FIXTURE_CASE_COUNT, "changed sealed public fixture denominator")
    fixture_relative = "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
    require(fixture.get("fixture") == fixture_relative, "changed sealed public fixture path")
    require(fixture.get("fixture_sha256") == PUBLIC_FILE_SHA256[fixture_relative], "changed sealed public fixture digest")
    require(fixture.get("failed") == 0, "sealed public fixture contains reference failures")
    require(parent.get("source_fixture") == fixture_relative, "original plan fixture was replaced")
    require(parent.get("source_fixture_sha256") == fixture.get("fixture_sha256"), "parent/fixture digest disagreement")
    require(parent.get("source_fixture_manifest_sha256") == PUBLIC_FILE_SHA256["performance/v7/evidence/rust-calibration-fixture-manifest.json"], "parent/fixture-manifest disagreement")
    require(parent.get("source_fixture_uncompressed_sha256")
            == fixture.get("uncompressed_fixture_sha256"),
            "parent/uncompressed-public-fixture digest disagreement")


def validate_candidate_proofs(base: dict[str, Any], strict: dict[str, Any],
                              locale: dict[str, Any], universal: dict[str, Any]) -> dict[str, Any]:
    """Validate synthetic or pinned proof objects without importing candidates."""
    require(all(isinstance(item, dict) for item in (base, strict, locale, universal)),
            "candidate qualification evidence is not an object")
    require(base.get("postfinal_schema") == "rebar-postfinal-from-scratch-audit-v5", "changed from-scratch audit schema")
    require(base.get("passed") is True and base.get("status") == "PASS"
            and base.get("result") == "PASS", "from-scratch candidate audit has not passed")
    require(base.get("verified_core_family_count", 0) >= 3, "fewer than three independent candidate families")
    base_families = base.get("families")
    require(isinstance(base_families, dict) and REQUIRED_FAMILIES <= base_families.keys(),
            "from-scratch audit does not qualify all three measured families")
    base_test = base.get("self_test")
    base_wrapper = base.get("postfinal_wrapper_self_test")
    require(isinstance(base_test, dict) and base_test.get("passed") is True
            and base_test.get("check_count") == 76 and base_test.get("failed") == [],
            "from-scratch verifier did not pass its exact 76 synthetic controls")
    require(isinstance(base_wrapper, dict) and base_wrapper.get("passed") is True
            and base_wrapper.get("status") == "PASS"
            and base_wrapper.get("check_count") == 198 and base_wrapper.get("failed") == [],
            "from-scratch verifier did not pass its exact 198 wrapper controls")
    require(base.get("audit_source_path") == "tools/postfinal_from_scratch_audit_v5.py"
            and base.get("audit_source_sha256")
            == PUBLIC_FILE_SHA256["tools/postfinal_from_scratch_audit_v5.py"],
            "from-scratch audit is not bound to its current producer")
    require(strict.get("schema") == "rebar-postfinal-no-delegation-audit-v5", "changed no-delegation audit schema")
    require(strict.get("passed") is True and strict.get("status") == "PASS"
            and strict.get("result") == "PASS", "no-delegation audit has not passed")
    require(strict.get("verified_core_family_count", 0) >= 3, "unqualified independent native families")
    strict_families = strict.get("families")
    require(isinstance(strict_families, dict) and REQUIRED_FAMILIES <= strict_families.keys(),
            "no-delegation audit does not qualify all three measured families")
    strict_test = strict.get("self_test")
    strict_wrapper = strict.get("postfinal_wrapper_self_test")
    require(isinstance(strict_test, dict) and strict_test.get("passed") is True
            and strict_test.get("check_count") == 32 and strict_test.get("failed") == [],
            "no-delegation verifier did not pass its exact 32 synthetic controls")
    require(strict.get("inherited_control_count") == 76,
            "no-delegation verifier lost its exact 76 inherited controls")
    require(isinstance(strict_wrapper, dict) and strict_wrapper.get("passed") is True
            and strict_wrapper.get("status") == "PASS"
            and strict_wrapper.get("check_count") == 676
            and strict_wrapper.get("failed") == [],
            "no-delegation verifier did not pass its exact 676 wrapper controls")
    require(strict.get("audit_source_path") == "tools/postfinal_no_delegation_audit_v5.py"
            and strict.get("audit_source_sha256")
            == PUBLIC_FILE_SHA256["tools/postfinal_no_delegation_audit_v5.py"],
            "no-delegation audit is not bound to its current producer")
    sources = strict.get("qualified_source_fingerprints")
    native = strict.get("native_elf_fingerprints")
    require(isinstance(sources, dict) and set(sources) == REQUIRED_SOURCE_PATHS,
            "candidate source family ownership changed")
    require(isinstance(native, dict) and set(native) == REQUIRED_NATIVE_ROLES,
            "candidate process/native role ownership changed")
    hex_characters = frozenset("0123456789abcdef")
    require(all(isinstance(value, str) and len(value) == 64
                and set(value) <= hex_characters for value in sources.values()),
            "invalid qualified candidate source fingerprint")
    require(all(isinstance(value, str) and len(value) == 64
                and set(value) <= hex_characters for value in native.values()),
            "invalid qualified candidate native fingerprint")
    native_provenance = strict.get("native_elf_provenance")
    require(isinstance(native_provenance, dict)
            and native_provenance.get("passed") is True
            and native_provenance.get("issues") == []
            and native_provenance.get("audited_binary_count") == 5
            and native_provenance.get("expected_binary_count") == 5,
            "no-delegation audit did not qualify exactly five native binaries")
    native_families = native_provenance.get("families")
    require(isinstance(native_families, dict)
            and set(native_families) == REQUIRED_FAMILIES,
            "native proof is missing an independently owned family")
    for family, expected_records in NATIVE_RECORD_ROLES.items():
        family_record = native_families.get(family)
        require(isinstance(family_record, dict)
                and family_record.get("passed") is True
                and family_record.get("issues") == [],
                f"native family {family} did not pass independent ownership")
        records = family_record.get("files")
        require(isinstance(records, dict) and set(records) == set(expected_records),
                f"native family {family} has changed binary roles")
        for record_name, role in expected_records.items():
            record = records.get(record_name)
            require(isinstance(record, dict)
                    and record.get("file") == REQUIRED_NATIVE_FILES[role]
                    and record.get("sha256") == native[role],
                    f"native family {family} has changed role/path provenance")
            require(record.get("forbidden_regex_symbols") == []
                    and record.get("cross_candidate_symbols") == [],
                    f"native family {family} delegates or crosses candidate boundaries")
    require(locale.get("schema") == "rebar-postfinal-cpython-public-locale-v1", "changed pinned locale oracle schema")
    require(locale.get("python") == "3.14.6" and locale.get("status") == "PASS"
            and locale.get("result") == "PASS", "pinned locale oracle has not passed")
    require(locale.get("goal_sha256") == PUBLIC_FILE_SHA256["GOAL.md"], "locale oracle is not bound to the immutable goal")
    require(locale.get("source_path") == "tools/postfinal_cpython_locale_oracle_v1.py"
            and locale.get("source_sha256")
            == PUBLIC_FILE_SHA256["tools/postfinal_cpython_locale_oracle_v1.py"],
            "locale oracle is not bound to its current producer")
    require(locale.get("timing_performed") is False and locale.get("performance") == "NOT MEASURED", "locale oracle contains performance")
    require(locale.get("qualified_source_fingerprints") == sources, "candidate source fingerprints disagree")
    require(locale.get("native_elf_fingerprints") == native, "candidate native roles disagree")
    locale_roles = locale.get("roles")
    require(isinstance(locale_roles, dict)
            and set(locale_roles) == {"re", "rust", "vm", "zig"},
            "locale oracle must qualify Python and all three measured families")
    for role, record in locale_roles.items():
        require(isinstance(record, dict) and record.get("module")
                == ("re" if role == "re" else f"candidates.{role}_candidate"),
                f"locale oracle module changed for {role}")
        require(record.get("methods") == 146 and record.get("passed") == 146
                and record.get("failed") == 0 and record.get("errors") == 0
                and record.get("skipped") == 0 and record.get("crashes") == 0
                and record.get("timeouts") == 0,
                f"locale oracle did not pass all 146 CPython methods for {role}")
        require(record.get("locale_compiled_passed") is True
                and record.get("locale_caching_passed") is True,
                f"compiled or cached locale semantics were not qualified for {role}")
        require(record.get("timing_performed") is False
                and record.get("performance") == "NOT MEASURED",
                f"locale role {role} contains timing")
        method_records = record.get("records")
        require(isinstance(method_records, list) and len(method_records) == 146,
                f"locale role {role} does not retain all 146 official method records")
        names: set[str] = set()
        for method in method_records:
            require(isinstance(method, dict) and method.get("status") == "passed"
                    and method.get("skipped") == 0,
                    f"locale role {role} has an unsuccessful official method")
            name = method.get("test")
            require(isinstance(name, str) and name and name not in names,
                    f"locale role {role} repeats or omits an official method")
            names.add(name)
        require({"ReTests.test_locale_compiled", "ReTests.test_locale_caching"}
                <= names,
                f"locale role {role} lacks the exact official compiled/cache tests")
    require(universal.get("schema") == "rebar-python-re-universal-public-oracle-v1", "changed independent public correctness schema")
    require(universal.get("python") == "3.14.6" and universal.get("status") == "PASS", "independent public correctness did not pass")
    require(universal.get("comparison_complete") is True and universal.get("mismatches") == 0, "independent public correctness mismatch")
    require(universal.get("cases") == ORIGINAL_CASE_COUNT, "independent public correctness denominator changed")
    require(universal.get("case_sha256") == UNIVERSAL_CASE_SHA256,
            "independent public correctness case fingerprint changed")
    require(set(universal.get("completed_candidates", ())) == REQUIRED_FAMILIES,
            "missing independently qualified C, Rust, or Zig candidate")
    require(set(universal.get("selected_candidates", ())) == REQUIRED_FAMILIES,
            "independent public correctness selected the wrong candidate families")
    require(universal.get("benchmark_or_timing_executed") is False, "performance entered public correctness evidence")
    require(universal.get("performance") == "NOT MEASURED", "public correctness evidence claims timing")
    require(universal.get("performance_fixtures_read") == 0, "public correctness evidence inspected performance fixtures")
    require(universal.get("external_regex_packages") == 0,
            "public correctness evidence loaded an external regex package")
    require(universal.get("observations_per_case") == 48
            and universal.get("observations_per_candidate") == 393_216
            and universal.get("total_comparisons") == 1_179_648
            and universal.get("planned_total_comparisons") == 1_179_648,
            "broad public correctness observation denominator changed")
    candidate_reports = universal.get("candidate_reports")
    require(isinstance(candidate_reports, dict)
            and set(candidate_reports) == REQUIRED_FAMILIES,
            "broad public correctness is missing a measured candidate")
    for family, record in candidate_reports.items():
        require(isinstance(record, dict) and record.get("status") == "PASS"
                and record.get("mismatches") == 0
                and record.get("case_sha256") == UNIVERSAL_CASE_SHA256
                and record.get("cases") == ORIGINAL_CASE_COUNT
                and record.get("benchmark_or_timing_executed") is False
                and record.get("performance_fixtures_read") == 0,
                f"broad public correctness did not qualify {family}")
    universal_audit = universal.get("audit")
    require(isinstance(universal_audit, dict),
            "broad public correctness has no source-bound audit")
    for source_key, hash_key, relative in (
        ("oracle_source_path", "oracle_source_sha256",
         "tools/python_re_universal_public_oracle_stage06.py"),
        ("guarded_worker_source_path", "guarded_worker_source_sha256",
         "tools/postfinal_no_delegation_audit_v1.py"),
        ("postfinal_audit_source_path", "postfinal_audit_source_sha256",
         "tools/postfinal_from_scratch_audit_v5.py"),
        ("postfinal_no_delegation_audit_source_path",
         "postfinal_no_delegation_audit_source_sha256",
         "tools/postfinal_no_delegation_audit_v5.py"),
        ("official_locale_source_path", "official_locale_source_sha256",
         "tools/postfinal_cpython_locale_oracle_v1.py"),
    ):
        require(universal_audit.get(source_key) == relative
                and universal_audit.get(hash_key) == PUBLIC_FILE_SHA256[relative],
                f"broad public correctness uses a stale producer: {relative}")
    require(set(universal_audit.get("selected_candidates", ())) == REQUIRED_FAMILIES,
            "broad public correctness audit changed selected families")
    require(universal_audit.get("previous_public_timing_evidence_read") is False,
            "broad public correctness audit read previous timing")
    family_sources = universal_audit.get("source_sha256")
    family_binaries = universal_audit.get("native_binary_sha256")
    require(isinstance(family_sources, dict)
            and set(family_sources) == REQUIRED_FAMILIES,
            "broad public correctness changed source families")
    merged_sources: dict[str, str] = {}
    for family, records in family_sources.items():
        require(isinstance(records, dict),
                f"broad public correctness source records changed for {family}")
        for relative, fingerprint in records.items():
            require(relative not in merged_sources,
                    "broad public correctness repeats an owned source")
            merged_sources[relative] = fingerprint
    require(merged_sources == sources,
            "broad public correctness uses stale or mixed candidate sources")
    require(isinstance(family_binaries, dict)
            and set(family_binaries) == REQUIRED_FAMILIES,
            "broad public correctness changed native families")
    for family, expected_records in NATIVE_RECORD_ROLES.items():
        records = family_binaries.get(family)
        require(isinstance(records, dict),
                f"broad public correctness native paths changed for {family}")
        expected = {REQUIRED_NATIVE_FILES[role]: native[role]
                    for role in expected_records.values()}
        require(records == expected,
                f"broad public correctness uses stale or mixed binaries for {family}")
    return {"sources": sources, "native": native}


def validate_stage10_pinset(pins: dict[str, str | None]) -> dict[str, str]:
    """Never infer or fabricate an unpublished Stage10 source or report hash."""
    expected_paths = {
        STAGE10_SOURCE_RELATIVE, STAGE10_PROTOCOL_RELATIVE,
        STAGE10_SELF_ORACLE_RELATIVE, STAGE10_ALL_CANDIDATES_RELATIVE,
    }
    require(isinstance(pins, dict) and set(pins) == expected_paths,
            "Stage10 must pin its exact producer, protocol, and both public reports")
    hexadecimal = frozenset("0123456789abcdef")
    checked: dict[str, str] = {}
    for relative in sorted(expected_paths):
        fingerprint = pins.get(relative)
        require(isinstance(fingerprint, str) and len(fingerprint) == 64
                and set(fingerprint) <= hexadecimal,
                f"Stage10 evidence is not yet final and published: {relative}")
        checked[relative] = fingerprint
    return checked


def validate_stage10_documents(reference: dict[str, Any], comparison: dict[str, Any],
                               pins: dict[str, str],
                               provenance: dict[str, Any],
                               reference_digest: Callable[[Any], str] = digest,
                               authenticated_provenance: dict[str, Any] | None = None,
                               ) -> dict[str, Any]:
    """Require a real dual-reference and all-three Stage10 qualification."""
    require(isinstance(reference, dict) and isinstance(comparison, dict),
            "Stage10 public correctness proof is not an object")
    self_required = {
        "schema": STAGE10_SELF_ORACLE_SCHEMA,
        "status": "PASS", "result": "PASS", "python": "3.14.6",
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "seed": STAGE10_SEED, "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": STAGE10_COHORTS,
        "cases": STAGE10_CASES,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "stdlib_checks": STAGE10_CASES * 2,
        "mismatches": 0, "failure_records": [],
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for field, expected in self_required.items():
        observed = reference.get(field)
        require(type(observed) is type(expected) and observed == expected,
                f"Stage10 dual-CPython self-oracle has not passed: {field}")
    reference_records = reference.get("baseline_records")
    require(isinstance(reference_records, list) and len(reference_records) == STAGE10_CASES,
            "Stage10 must preserve all 3,584 actual CPython reference records")
    expected_record_ids = [
        f"{cohort}:{index:04d}"
        for cohort, count in STAGE10_COHORT_CASES.items()
        for index in range(count)
    ]
    require(all(isinstance(record, dict) for record in reference_records)
            and [record.get("id") for record in reference_records]
            == expected_record_ids,
            "Stage10 did not preserve all exact ordered public matrix obligations")
    reference_hash = reference_digest(reference_records)
    require(reference.get("baseline_record_sha256") == reference_hash
            and reference.get("second_record_sha256") == reference_hash,
            "Stage10 independent CPython references disagree")
    cohort_cases = reference.get("cohort_cases")
    require(isinstance(cohort_cases, dict)
            and cohort_cases == STAGE10_COHORT_CASES,
            "Stage10 does not retain all eight exact weighted public obligation cohorts")
    all_required = {
        "schema": STAGE10_ALL_CANDIDATES_SCHEMA,
        "status": "PASS", "result": "PASS", "selected": "all",
        "comparison_complete": True, "python": "3.14.6",
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "seed": STAGE10_SEED, "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": STAGE10_COHORTS,
        "cases_per_candidate": STAGE10_CASES,
        "candidate_checks": STAGE10_CASES * len(REQUIRED_FAMILIES),
        "previous_public_cases": ORIGINAL_CASE_COUNT,
        "previous_public_comparisons": 1_179_648,
        "combined_public_comparisons": 1_190_400,
        "mismatches": 0,
        "self_oracle_path": STAGE10_SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": pins[STAGE10_SELF_ORACLE_RELATIVE],
        "external_regex_packages": 0,
        "candidate_cross_delegation": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for field, expected in all_required.items():
        observed = comparison.get(field)
        require(type(observed) is type(expected) and observed == expected,
                f"Stage10 all-family public correctness has not passed: {field}")
    require(set(comparison.get("selected_candidates", ())) == REQUIRED_FAMILIES
            and set(comparison.get("completed_candidates", ())) == REQUIRED_FAMILIES,
            "Stage10 omitted an independently implemented candidate")
    require(comparison.get("cohort_cases") == cohort_cases,
            "Stage10 candidate cohorts differ from the two actual CPython references")
    stage_provenance = comparison.get("current_provenance")
    require(isinstance(stage_provenance, dict)
            and reference.get("current_provenance") == stage_provenance,
            "Stage10 baseline and candidate source provenance disagree")
    if authenticated_provenance is not None:
        require(stage_provenance == authenticated_provenance,
                "Stage10 evidence changed its producer-authenticated provenance")
    require(stage_provenance.get("source_path") == STAGE10_SOURCE_RELATIVE
            and stage_provenance.get("source_sha256")
            == pins[STAGE10_SOURCE_RELATIVE]
            and stage_provenance.get("protocol_path") == STAGE10_PROTOCOL_RELATIVE
            and stage_provenance.get("protocol_sha256")
            == pins[STAGE10_PROTOCOL_RELATIVE],
            "Stage10 proof is not bound to its exact finalized producer")
    require(stage_provenance.get("observation_domain") == STAGE10_OBSERVATION_DOMAIN,
            "Stage10 metadata uses a different observation domain")
    require(stage_provenance.get("official_methods_per_role") == 146
            and stage_provenance.get("official_role_count") == 4
            and stage_provenance.get("official_skipped") == 0,
            "Stage10 proof is not bound to all genuine official locale obligations")
    preserved_failures = {
        "previous_failed_source_path":
            "tools/python_re_universal_public_oracle_stage07.py",
        "previous_failed_source_sha256": PUBLIC_FILE_SHA256[
            "tools/python_re_universal_public_oracle_stage07.py"],
        "previous_failed_protocol_path":
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md",
        "previous_failed_protocol_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md"],
        "previous_self_oracle_failure_path":
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v7-self-oracle-failures.json",
        "previous_self_oracle_failure_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v7-self-oracle-failures.json"],
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
        "previous_stage08_source_path":
            "tools/python_re_universal_public_oracle_stage08.py",
        "previous_stage08_source_sha256": PUBLIC_FILE_SHA256[
            "tools/python_re_universal_public_oracle_stage08.py"],
        "previous_stage08_protocol_path":
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md",
        "previous_stage08_protocol_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md"],
        "previous_stage08_self_oracle_path":
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v8-self-oracle.json",
        "previous_stage08_self_oracle_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v8-self-oracle.json"],
        "previous_stage08_rust_failure_path":
            "candidates/evidence/"
            "python-re-universal-public-oracle-v8-rust-failures.json",
        "previous_stage08_rust_failure_sha256": PUBLIC_FILE_SHA256[
            "candidates/evidence/"
            "python-re-universal-public-oracle-v8-rust-failures.json"],
        "previous_stage08_rust_failure_count": 256,
        "previous_stage08_rust_matching_observations": 3_328,
        "previous_stage08_rust_failure_preserved": True,
    }
    for field, expected in preserved_failures.items():
        observed = stage_provenance.get(field)
        require(type(observed) is type(expected) and observed == expected,
                f"Stage10 concealed or changed a genuine preserved failure: {field}")
    stage_sources = stage_provenance.get("source_sha256_by_family")
    stage_native = stage_provenance.get("native_sha256_by_family")
    require(isinstance(stage_sources, dict) and set(stage_sources) == REQUIRED_FAMILIES,
            "Stage10 candidate source families are incomplete")
    flattened: dict[str, str] = {}
    for family, entries in stage_sources.items():
        require(isinstance(entries, dict),
                f"Stage10 candidate source mapping changed for {family}")
        for relative, fingerprint in entries.items():
            require(relative not in flattened, "Stage10 repeats an owned candidate source")
            flattened[relative] = fingerprint
    require(flattened == provenance.get("sources"),
            "Stage10 candidate sources differ from the current strict V5 proof")
    require(isinstance(stage_native, dict) and set(stage_native) == REQUIRED_FAMILIES,
            "Stage10 candidate native families are incomplete")
    reports = comparison.get("candidate_reports")
    require(isinstance(reports, dict) and set(reports) == REQUIRED_FAMILIES,
            "Stage10 must pass all three independent candidate families")
    for family, expected_roles in NATIVE_RECORD_ROLES.items():
        expected_native = {
            REQUIRED_NATIVE_FILES[role]: provenance["native"][role]
            for role in expected_roles.values()
        }
        require(stage_native.get(family) == expected_native,
                f"Stage10 native provenance changed for {family}")
        record = reports.get(family)
        require(isinstance(record, dict) and record.get("candidate") == family
                and record.get("module") == f"candidates.{family}_candidate"
                and record.get("status") == "PASS"
                and record.get("cases") == STAGE10_CASES
                and record.get("cohort_cases") == cohort_cases
                and record.get("mismatches") == 0
                and record.get("failure_records") == []
                and record.get("failures_recorded") == 0
                and record.get("native_binary_sha256") == expected_native
                and record.get("benchmark_or_timing_executed") is False
                and record.get("holdout_cases_read") == 0
                and record.get("performance") == "NOT MEASURED",
                f"Stage10 did not completely qualify independent {family}")
        guard = record.get("guard")
        require(isinstance(guard, dict) and guard.get("enabled") is True
                and guard.get("family") == family
                and guard.get("stdlib_re_blocked") is True
                and guard.get("cpython_sre_blocked") is True
                and guard.get("third_party_regex_blocked") is True
                and guard.get("cross_family_blocked") is True
                and guard.get("foreign_dynamic_libraries_blocked") is True
                and guard.get("cached_regex_aliases_poisoned") == 10
                and guard.get("native_loader_aliases_blocked")
                == list(STAGE10_NATIVE_LOADER_ALIASES),
                f"Stage10 weakened the independent owned-engine guard for {family}")
        expected_candidate_modules = {
            "rust": ["candidates._rust_bridge", "candidates.rust_candidate"],
            "vm": ["candidates._vm_native", "candidates.vm_candidate"],
            "zig": ["candidates._zig_bridge", "candidates.zig_candidate"],
        }
        require(guard.get("loaded_candidate_modules")
                == expected_candidate_modules[family],
                f"Stage10 imported an unexpected engine for {family}")
        prohibited = guard.get("prohibited_modules")
        require(isinstance(prohibited, list)
                and {"re", "_sre", "regex", "re2", "pcre", "pcre2"}
                <= set(prohibited)
                and all(f"candidates.{peer}_candidate" in prohibited
                        for peer in REQUIRED_FAMILIES if peer != family),
                f"Stage10 did not prohibit all external and peer engines for {family}")
        metadata = guard.get("isolated_public_metadata")
        require(isinstance(metadata, dict)
                and metadata.get("enabled") is True
                and metadata.get("schema") == STAGE10_METADATA_SCHEMA
                and metadata.get("source_sha256")
                == pins[STAGE10_SOURCE_RELATIVE]
                and metadata.get("role") == family
                and metadata.get("surface_cases") == 256
                and isinstance(metadata.get("record_sha256"), str)
                and len(metadata["record_sha256"]) == 64
                and metadata.get("production_matching_executed") is False
                and metadata.get("metadata_and_matcher_processes_distinct")
                is True
                and metadata.get("matcher_inspect_loaded") is False
                and metadata.get("matcher_tokenizer_loaded") is False,
                f"Stage10 did not isolate source-bound metadata for {family}")
    require(comparison.get("locales") == reference.get("locales"),
            "Stage10 candidate locales differ from the actual CPython reference")
    return {
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "self_oracle_path": STAGE10_SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": pins[STAGE10_SELF_ORACLE_RELATIVE],
        "all_candidates_path": STAGE10_ALL_CANDIDATES_RELATIVE,
        "all_candidates_sha256": pins[STAGE10_ALL_CANDIDATES_RELATIVE],
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": STAGE10_COHORTS,
        "cases": STAGE10_CASES,
        "stdlib_checks": STAGE10_CASES * 2,
        "candidate_checks": STAGE10_CASES * len(REQUIRED_FAMILIES),
    }


def verify_stage10_public_provenance(provenance: dict[str, Any],
                                     pins: dict[str, str]) -> dict[str, Any]:
    """Read only four exact, root-finalized Stage10 public files."""
    root = ROOT.resolve()
    for relative, expected in sorted(pins.items()):
        relative_path = Path(relative)
        require(not relative_path.is_absolute() and ".." not in relative_path.parts
                and str(relative_path) == relative,
                f"Stage10 proof path is not exact: {relative}")
        path = ROOT / relative_path
        try:
            resolved = path.resolve(strict=True)
            inside = resolved.relative_to(root)
        except (OSError, ValueError) as error:
            raise PublicExpansionError(f"required passing Stage10 proof is absent: {relative}") from error
        require(inside == relative_path and not path.is_symlink(),
                f"Stage10 proof path was replaced or escaped: {relative}")
        require(bounded_source_file_sha256(path, MAX_OWNED_ARTIFACT_BYTES,
                                          f"Stage10 proof {relative}") == expected,
                f"Stage10 proof is stale or has not been frozen: {relative}")

    def read_stage(relative: str) -> dict[str, Any]:
        try:
            document = json.loads((ROOT / relative).read_bytes())
        except (OSError, UnicodeError, ValueError) as error:
            raise PublicExpansionError(f"invalid published Stage10 proof: {relative}") from error
        require(isinstance(document, dict), f"Stage10 proof is not an object: {relative}")
        return document

    reference = read_stage(STAGE10_SELF_ORACLE_RELATIVE)
    comparison = read_stage(STAGE10_ALL_CANDIDATES_RELATIVE)
    before_candidates = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    source = ROOT / STAGE10_SOURCE_RELATIVE
    specification = importlib.util.spec_from_file_location(
        "rebar_frozen_public_contract_v10", source
    )
    require(specification is not None and specification.loader is not None,
            "cannot import the exact source-bound Stage10 public validator")
    module = importlib.util.module_from_spec(specification)
    try:
        specification.loader.exec_module(module)
        require(module.SOURCE_RELATIVE == STAGE10_SOURCE_RELATIVE
                and module.PROTOCOL_RELATIVE == STAGE10_PROTOCOL_RELATIVE
                and module.SELF_ORACLE_SCHEMA == STAGE10_SELF_ORACLE_SCHEMA
                and module.ALL_CANDIDATE_SCHEMA == STAGE10_ALL_CANDIDATES_SCHEMA
                and module.MATRIX_SHA256 == STAGE10_MATRIX_SHA256,
                "source-bound Stage10 validator changed its public contract")
        with module._stage10_context():
            authenticated = module._authenticate_current_provenance()
            restored_reference = module.previous._restore_portable(reference)
            verified_reference = module.stage07._validate_self_oracle(
                restored_reference, authenticated
            )
            restored_comparison = module.previous._restore_portable(comparison)
            result = validate_stage10_documents(
                verified_reference,
                restored_comparison,
                pins,
                provenance,
                reference_digest=module.previous.digest,
                authenticated_provenance=authenticated,
            )
    except PublicExpansionError:
        raise
    except Exception as error:
        raise PublicExpansionError(
            "the frozen Stage10 canonical self-oracle or authenticated proof failed"
        ) from error
    require({
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    } == before_candidates,
        "the Stage10 correctness validator imported a candidate engine")
    return result


def verify_public_provenance() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    # An unpublished Stage10 pin fails here, before any fixture is read or
    # either independent V8 CPython worker can be constructed.
    stage10_pins = validate_stage10_pinset(STAGE10_PINNED_SHA256)
    deferred_fixture_inputs = {
        "performance/v7/evidence/rust-calibration-fixture-manifest.json",
        "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
    }
    for relative, expected in PUBLIC_FILE_SHA256.items():
        if relative in deferred_fixture_inputs:
            continue
        path = ROOT / relative
        require(path.is_file(), f"missing pinned public evidence: {relative}")
        require(source_file_sha256(path) == expected, f"stale pinned public evidence: {relative}")
    base = read_pinned_json("candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json")
    strict = read_pinned_json("candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json")
    locale = read_pinned_json("oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json")
    universal = read_pinned_json("candidates/evidence/python-re-universal-public-oracle-v6-all.json")
    provenance = validate_candidate_proofs(base, strict, locale, universal)
    verify_live_owned_artifacts(provenance)
    provenance["stage10"] = verify_stage10_public_provenance(provenance, stage10_pins)
    for relative in sorted(deferred_fixture_inputs):
        path = ROOT / relative
        require(path.is_file(), f"missing pinned public fixture: {relative}")
        require(source_file_sha256(path) == PUBLIC_FILE_SHA256[relative],
                f"stale pinned public fixture: {relative}")
    parent = read_pinned_json("performance/postfinal-public-v6/manifest.json")
    fixture = read_pinned_json("performance/v7/evidence/rust-calibration-fixture-manifest.json")
    validate_public_source_documents(parent, fixture)
    return parent, fixture, provenance


def verify_live_owned_artifacts(provenance: dict[str, Any]) -> dict[str, Any]:
    """Hash exact report-declared source files and the five mapped native ELFs."""
    require(isinstance(provenance, dict), "live owned provenance is not an object")
    sources = provenance.get("sources")
    native = provenance.get("native")
    require(isinstance(sources, dict) and set(sources) == REQUIRED_SOURCE_PATHS,
            "live owned source set changed")
    require(isinstance(native, dict) and set(native) == REQUIRED_NATIVE_ROLES,
            "live owned native role set changed")
    root = ROOT.resolve()

    def check_relative(relative: str, expected: str, label: str) -> None:
        require(isinstance(relative, str) and relative.startswith("candidates/"),
                f"{label} escaped the candidate source root")
        relative_path = Path(relative)
        require(not relative_path.is_absolute()
                and ".." not in relative_path.parts
                and str(relative_path) == relative,
                f"{label} uses a noncanonical owned path")
        path = ROOT / relative_path
        try:
            resolved = path.resolve(strict=True)
            inside = resolved.relative_to(root)
        except (OSError, ValueError) as error:
            raise PublicExpansionError(f"{label} escaped its exact owned path") from error
        require(inside == relative_path and not path.is_symlink(),
                f"{label} uses an owned-path symbolic link")
        require(bounded_source_file_sha256(path, MAX_OWNED_ARTIFACT_BYTES, label)
                == expected, f"stale live owned artifact: {relative}")

    for relative, fingerprint in sorted(sources.items()):
        check_relative(relative, fingerprint, "qualified candidate source")
    for role, relative in sorted(REQUIRED_NATIVE_FILES.items()):
        check_relative(relative, native[role], f"qualified native role {role}")
    return {"verified_source_count": len(sources),
            "verified_native_count": len(native)}


def load_public_fixture(fixture_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    positions: set[int] = set()
    uncompressed = hashlib.sha256()
    fixture_path = ROOT / "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
    with gzip.open(fixture_path, "rb") as stream:
        for raw in stream:
            uncompressed.update(raw)
            document = decode_public_fixture_line(raw)
            require(document.get("schema") == FIXTURE_SCHEMA, "changed public fixture record schema")
            require(document.get("cohort") == "calibration", "non-public record entered calibration fixture")
            position = document["position"]
            require(isinstance(position, int) and not isinstance(position, bool) and position >= 0, "invalid public fixture position")
            require(position not in positions, "duplicate public fixture position")
            positions.add(position)
            case, expected = document["case"], document["expected"]
            require(isinstance(case, dict) and isinstance(expected, dict), "invalid public case or reference answer")
            require(case.get("cohort") == expected.get("cohort") == "calibration", "non-public case or reference answer")
            identifier = case.get("id")
            require(isinstance(identifier, str) and identifier and identifier not in rows, "duplicate or missing public case identifier")
            require(expected.get("id") == identifier, "public case and answer identifiers disagree")
            require(case.get("category") == expected.get("category"), "public case and answer categories disagree")
            require(case.get("api") in PUBLIC_OPERATIONS, "unknown public operation")
            require(case.get("weight") == 1, "public case weight changed")
            require(digest(expected.get("result")) == expected.get("result_sha256"), "corrupt public reference answer")
            require(source_kind(case) in {"text", "bytes", "bytearray", "memoryview"},
                    "public fixture case has an unsupported input type")
            subject = unpack(case.get("string"))
            require(subject is None or isinstance(subject, (str, bytes, bytearray, memoryview)), "unsupported public subject")
            require(subject is None or len(subject) <= SUBJECT_LIMIT, "public subject exceeds its frozen limit")
            require(result_cardinality(expected["result"]) <= RESULT_LIMIT, "public result exceeds its frozen limit")
            rows[identifier] = {"position": position, "case": case, "expected": expected}
    require(len(rows) == FIXTURE_CASE_COUNT, "changed public fixture row denominator")
    require(uncompressed.hexdigest() == fixture_manifest.get("uncompressed_fixture_sha256"), "changed uncompressed public fixture")
    return rows


def result_cardinality(result: Any) -> int:
    if result is None:
        return 0
    return len(result) if isinstance(result, (list, tuple)) else 1


def result_density(result: Any) -> str:
    count = result_cardinality(result)
    return "none" if count == 0 else "one" if count == 1 else "few" if count <= 8 else "many"


def source_kind(case: dict[str, Any]) -> str:
    """Match the frozen fixture contract, including buffer-view subjects."""
    require(isinstance(case, dict), "public source-kind case is not an object")
    explicit = case.get("subject_kind")
    require(explicit is None or explicit in {"text", "bytes", "bytearray", "memoryview"},
            "unsupported public subject-kind declaration")
    if case.get("api") in {"compile", "escape"}:
        value = unpack(case.get("pattern"))
    else:
        value = unpack(case.get("string"))
    if explicit is not None:
        if explicit == "text":
            require(isinstance(value, str), "text subject-kind changed its value type")
        else:
            require(isinstance(value, (bytes, bytearray, memoryview)),
                    "binary subject-kind changed its value type")
        return explicit
    if isinstance(value, str):
        return "text"
    if isinstance(value, bytes):
        return "bytes"
    if isinstance(value, bytearray):
        return "bytearray"
    if isinstance(value, memoryview):
        return "memoryview"
    raise PublicExpansionError("cannot derive the frozen public source kind")


def effective_subject(case: dict[str, Any]) -> Any:
    value = unpack(case.get("string"))
    declared = case.get("subject_kind")
    if declared == "bytearray":
        require(isinstance(value, (bytes, bytearray, memoryview)),
                "bytearray public subject has no binary source")
        return bytearray(value)
    if declared == "memoryview":
        require(isinstance(value, (bytes, bytearray, memoryview)),
                "memoryview public subject has no binary source")
        return memoryview(value)
    if declared == "bytes":
        require(isinstance(value, (bytes, bytearray, memoryview)),
                "bytes public subject has no binary source")
        return bytes(value)
    if declared == "text":
        require(isinstance(value, str), "text public subject has no text source")
    return value


def append_public_pattern(pattern: Any, suffix: str) -> Any:
    require(isinstance(suffix, str) and suffix.isascii(), "non-ASCII public pattern variation")
    if isinstance(pattern, str):
        return pattern + suffix
    require(isinstance(pattern, dict), "unsupported public pattern representation")
    require(pattern.get(PACKING_MARKER) == "bytes", "public pattern is not immutable bytes")
    require(set(pattern) == {PACKING_MARKER, "hex"}, "invalid encoded public pattern")
    try:
        payload = bytes.fromhex(pattern["hex"])
    except (TypeError, ValueError) as error:
        raise PublicExpansionError("invalid encoded public pattern") from error
    return {PACKING_MARKER: "bytes", "hex": (payload + suffix.encode("ascii")).hex()}


def make_variant(template: dict[str, Any], serial: int) -> dict[str, Any]:
    require(isinstance(serial, int) and not isinstance(serial, bool) and serial >= 0, "invalid public variant number")
    case = template["case"]
    label = f"{case['category']}:{case['id']}:{serial}"
    token = seed_key(label)[0].hex()[:20]
    suffix = f"-r8-{token}" if case["api"] == "escape" else f"(?#r8-{token})"
    variant = dict(case)
    variant["id"] = f"cal.public.v8.{token}"
    variant["pattern"] = append_public_pattern(case["pattern"], suffix)
    require(variant.get("cohort") == "calibration", "generated case changed its public cohort")
    require(variant["category"] == case["category"], "generated case changed its category")
    require(variant["api"] == case["api"], "generated case changed its operation")
    require(variant["lifecycle"] == case["lifecycle"], "generated case changed its lifecycle")
    require(variant["flags"] == case["flags"], "generated case changed its flags")
    require(variant["string"] == case["string"], "generated case changed its subject")
    require({key: value for key, value in variant.items() if key not in {"id", "pattern"}}
            == {key: value for key, value in case.items() if key not in {"id", "pattern"}},
            "generated case changed its source category semantics")
    return variant


def select_public_cases(parent: dict[str, Any], fixture: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    original = parent.get("selected_cases")
    require(isinstance(original, list) and len(original) == ORIGINAL_CASE_COUNT, "missing exact 8,192 original public cases")
    originals: list[dict[str, Any]] = []
    identities: set[str] = set()
    identifiers: set[str] = set()
    by_category: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in fixture.values():
        by_category[record["case"]["category"]].append(record)
    require(len(by_category) == CATEGORY_COUNT, "changed original public category universe")
    category_counts: collections.Counter[str] = collections.Counter()
    for descriptor in original:
        require(isinstance(descriptor, dict), "invalid original public case descriptor")
        identifier = descriptor.get("case")
        require(isinstance(identifier, str) and identifier in fixture, "original public case is not in its pinned fixture")
        record = fixture[identifier]
        case = record["case"]
        require(descriptor.get("cohort") == case["cohort"] == "calibration", "original public case changed cohort")
        require(descriptor.get("category") == case["category"], "original public case changed category")
        require(descriptor.get("api") == case["api"], "original public case changed operation")
        require(descriptor.get("lifecycle") == case["lifecycle"], "original public case changed lifecycle")
        require(descriptor.get("input") == source_kind(case),
                "original public case changed its text, bytes, or buffer input")
        require(descriptor.get("expected_result_sha256") == record["expected"]["result_sha256"], "original public reference answer changed")
        identity = semantic_identity(case)
        require(identity not in identities, "duplicate original public semantic identity")
        require(identifier not in identifiers, "duplicate original public case")
        identities.add(identity)
        identifiers.add(identifier)
        category_counts[case["category"]] += 1
        originals.append({"case": case, "expected": record["expected"], "descriptor": descriptor, "source_id": identifier, "generated": False})
    require(set(category_counts) == set(by_category), "an original public category disappeared")
    require(all(count <= CASES_PER_CATEGORY for count in category_counts.values()), "original public category exceeds its new allocation")
    generated: list[dict[str, Any]] = []
    for category in sorted(by_category):
        templates = sorted(by_category[category], key=lambda item: seed_key(f"template:{category}:{item['case']['id']}"))
        require(bool(templates), "public category has no source template")
        serial = 0
        while category_counts[category] < CASES_PER_CATEGORY:
            template = templates[serial % len(templates)]
            variant = make_variant(template, serial)
            identity = semantic_identity(variant)
            require(identity not in identities, "generated public semantic collision")
            require(variant["id"] not in identifiers, "generated public identifier collision")
            identities.add(identity)
            identifiers.add(variant["id"])
            category_counts[category] += 1
            generated.append({"case": variant, "expected": None, "descriptor": None,
                              "source_id": template["case"]["id"], "generated": True})
            serial += 1
    require(len(originals) == ORIGINAL_CASE_COUNT, "the exact original public case population changed")
    require(len(originals) + len(generated) == CASE_COUNT, "the expanded public denominator changed")
    require(len(identities) == CASE_COUNT and len(identifiers) == CASE_COUNT, "expanded public identity collision")
    require(len(category_counts) == CATEGORY_COUNT, "expanded public category disappeared")
    require(all(count == CASES_PER_CATEGORY for count in category_counts.values()), "expanded public categories are not equally weighted")
    return originals + generated


def match_snapshot(match: Any) -> Any:
    if match is None:
        return None
    return {
        "span": snapshot(match.span()),
        "groups": snapshot(match.groups()),
        "groupdict": snapshot(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
    }


def replacement(case: dict[str, Any]) -> Any:
    value = case.get("repl")
    if isinstance(value, dict) and value.get("callable") == "upper_bracket":
        return lambda match: b"[" + match.group(0).upper() + b"]" if isinstance(match.group(0), bytes) else "[" + match.group(0).upper() + "]"
    if isinstance(value, dict) and value.get("callable") == "lower_bracket":
        return lambda match: b"[" + match.group(0).lower() + b"]" if isinstance(match.group(0), bytes) else "[" + match.group(0).lower() + "]"
    require(not isinstance(value, dict) or PACKING_MARKER in value, "unknown public callable replacement")
    return unpack(value)


def oracle_result(case: dict[str, Any]) -> Any:
    """Called solely in a pinned, isolated CPython oracle-worker process."""
    require(sys.flags.isolated == 1, "CPython oracle worker is not isolated")
    require(tuple(sys.version_info[:3]) == (3, 14, 6), "CPython oracle worker version changed")
    require(Path(sys.executable).resolve() == PINNED_PYTHON.resolve(), "CPython oracle worker interpreter changed")
    require(not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "candidate imported into the CPython oracle")
    import re as stdlib_re

    flags = 0
    for name in case["flags"]:
        require(name in {"A", "I", "M", "S", "X"}, "unsupported public regex flag")
        flags |= getattr(stdlib_re, name)
    api = case["api"]
    pattern = unpack(case["pattern"])
    if api == "escape":
        return snapshot(stdlib_re.escape(pattern))
    compiled = stdlib_re.compile(pattern, flags)
    if api == "compile":
        return snapshot({"pattern": compiled.pattern, "flags": compiled.flags,
                         "groups": compiled.groups, "groupindex": dict(compiled.groupindex)})
    subject = effective_subject(case)
    window: list[Any] = [subject]
    if "pos" in case:
        window.append(case["pos"])
    if "endpos" in case:
        require("pos" in case, "public case supplied endpos without pos")
        window.append(case["endpos"])
    if api in {"search", "match", "fullmatch"}:
        return match_snapshot(getattr(compiled, api)(*window))
    if api == "findall":
        return snapshot(compiled.findall(*window))
    if api == "finditer":
        return [match_snapshot(item) for item in compiled.finditer(*window)]
    if api == "split":
        return snapshot(compiled.split(subject, case.get("maxsplit", 0)))
    if api == "sub":
        return snapshot(compiled.sub(replacement(case), subject, case.get("count", 0)))
    if api == "subn":
        return snapshot(compiled.subn(replacement(case), subject, case.get("count", 0)))
    if api == "scanner":
        scanner = compiled.scanner(*window)
        matches = []
        while (item := scanner.search()) is not None:
            matches.append(match_snapshot(item))
            require(len(matches) <= RESULT_LIMIT, "public scanner exceeded its frozen result limit")
        return matches
    if api == "match-surface":
        item = compiled.search(*window)
        require(item is not None, "public match-surface lost its source match")
        return snapshot([
            item.group(0), item.groups(), item.groupdict(),
            [item.span(group) for group in range(compiled.groups + 1)],
            item.lastgroup, item.expand(unpack(case["expand"])),
        ])
    raise PublicExpansionError(f"unsupported public operation: {api}")


def run_oracle_worker(role: str) -> None:
    require(role in {"first", "second"}, "unknown independent public oracle role")
    require(sys.flags.isolated == 1, "public oracle worker must use isolated Python")
    try:
        request = json.loads(sys.stdin.buffer.read())
    except (UnicodeError, ValueError) as error:
        raise PublicExpansionError("invalid public oracle worker request") from error
    require(isinstance(request, dict) and request.get("domain") == SEED_DOMAIN, "public oracle worker seed domain changed")
    cases = request.get("cases")
    require(isinstance(cases, list) and len(cases) == CASE_COUNT, "public oracle worker denominator changed")
    answers = []
    for record in cases:
        require(isinstance(record, dict), "invalid public oracle worker case")
        require(record.get("cohort") == "calibration", "non-public case reached the CPython oracle")
        result = oracle_result(record)
        require(result_cardinality(result) <= RESULT_LIMIT, "public CPython answer exceeded its result bound")
        answers.append({"id": record["id"], "result": result, "result_sha256": digest(result)})
    response = {"schema": ORACLE_SCHEMA, "role": role, "python": "3.14.6",
                "domain": SEED_DOMAIN, "cases": len(answers), "answers": answers,
                "candidate_imports": [], "timing": "NOT MEASURED"}
    sys.stdout.buffer.write(json_bytes(response) + b"\n")


def require_independent_cpython_answers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    require(len(rows) == CASE_COUNT, "public self-oracle population changed")
    request = json_bytes({"domain": SEED_DOMAIN, "cases": [row["case"] for row in rows]})
    verified: list[list[dict[str, Any]]] = []
    for role in ("first", "second"):
        command = [str(PINNED_PYTHON), "-I", "-B", str(Path(__file__).resolve()),
                   "--oracle-worker", "--role", role]
        try:
            completed = subprocess.run(command, input=request, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, check=False)
        except OSError as error:
            raise PublicExpansionError("cannot start the pinned isolated CPython self-oracle") from error
        require(completed.returncode == 0, f"isolated CPython self-oracle {role} failed")
        try:
            response = json.loads(completed.stdout)
        except (UnicodeError, ValueError) as error:
            raise PublicExpansionError(f"invalid isolated CPython self-oracle {role} answer") from error
        require(isinstance(response, dict), "CPython self-oracle answer is not an object")
        require(response.get("schema") == ORACLE_SCHEMA and response.get("role") == role,
                "isolated CPython self-oracle role changed")
        require(response.get("python") == "3.14.6" and response.get("domain") == SEED_DOMAIN,
                "isolated CPython self-oracle provenance changed")
        require(response.get("cases") == CASE_COUNT and response.get("candidate_imports") == [],
                "isolated CPython self-oracle was contaminated")
        require(response.get("timing") == "NOT MEASURED", "self-oracle claimed timing")
        answers = response.get("answers")
        require(isinstance(answers, list) and len(answers) == CASE_COUNT,
                "isolated CPython self-oracle answer denominator changed")
        verified.append(answers)
    require(verified[0] == verified[1], "independent CPython self-oracle workers disagree")
    for row, answer in zip(rows, verified[0], strict=True):
        require(isinstance(answer, dict) and answer.get("id") == row["case"]["id"],
                "CPython self-oracle case order or identifier changed")
        require(digest(answer.get("result")) == answer.get("result_sha256"),
                "CPython self-oracle answer digest changed")
        if not row["generated"]:
            require(answer["result"] == row["expected"]["result"]
                    and answer["result_sha256"] == row["expected"]["result_sha256"],
                    "CPython self-oracle disagrees with an original frozen public answer")
    return verified[0]


def build_manifest(parent: dict[str, Any], rows: list[dict[str, Any]],
                   answers: list[dict[str, Any]], provenance: dict[str, Any],
                   program: dict[str, str]) -> dict[str, Any]:
    require(len(rows) == len(answers) == CASE_COUNT, "expanded public manifest denominator changed")
    require(isinstance(program, dict)
            and set(program) == {"runner_path", "runner_sha256",
                                 "protocol_path", "protocol_sha256"},
            "expanded public runner/protocol provenance is incomplete")
    require(program.get("runner_path") == "tools/postfinal_public_expansion_v8.py"
            and program.get("protocol_path")
            == "performance/postfinal-public-v8/PROTOCOL.md",
            "expanded public runner or protocol path changed")
    hexadecimal = frozenset("0123456789abcdef")
    require(all(isinstance(program.get(key), str)
                and len(program[key]) == 64
                and set(program[key]) <= hexadecimal
                for key in ("runner_sha256", "protocol_sha256")),
            "expanded public runner/protocol fingerprint is invalid")
    descriptors = list(parent["selected_cases"])
    complete: list[dict[str, Any]] = []
    identities: list[str] = []
    observed_identities: set[str] = set()
    operations: collections.Counter[str] = collections.Counter()
    categories: collections.Counter[str] = collections.Counter()
    for row, answer in zip(rows, answers, strict=True):
        case = row["case"]
        require(answer["id"] == case["id"], "expanded public answer identifier changed")
        identity = semantic_identity(case)
        require(identity not in observed_identities,
                "expanded public manifest repeats a semantic identity")
        identities.append(identity)
        observed_identities.add(identity)
        operations[case["api"]] += 1
        categories[case["category"]] += 1
        expected = {"cohort": "calibration", "id": case["id"],
                    "category": case["category"], "result": answer["result"],
                    "result_sha256": answer["result_sha256"]}
        if row["generated"]:
            source = row["source_id"]
            descriptors.append({
                "case": case["id"], "cohort": "calibration", "category": case["category"],
                "api": case["api"], "lifecycle": case["lifecycle"],
                "input": source_kind(case),
                "source_case": source, "expected_result_sha256": answer["result_sha256"],
                "frozen_operations": case["ops"],
                "subject_length": len(unpack(case["string"])) if case["string"] is not None else 0,
                "result_count": result_cardinality(answer["result"]),
                "result_density": result_density(answer["result"]),
                "selection_reasons": ["public-development-v8-balanced-category"],
            })
        complete.append({"case": case, "expected": expected,
                         "source_case": row["source_id"],
                         "semantic_identity": identity,
                         "generated": row["generated"]})
    require(descriptors[:ORIGINAL_CASE_COUNT] == parent["selected_cases"],
            "the exact original public case descriptors were changed")
    require(len(descriptors) == CASE_COUNT and len(complete) == CASE_COUNT,
            "expanded public manifest case count changed")
    require(len(identities) == CASE_COUNT and len(observed_identities) == CASE_COUNT,
            "expanded public manifest identity evidence changed")
    require(set(operations) == set(PUBLIC_OPERATIONS), "expanded public suite lost an operation")
    require(sum(operations.values()) == CASE_COUNT, "expanded operation denominators do not sum")
    require(len(categories) == CATEGORY_COUNT and all(n == CASES_PER_CATEGORY for n in categories.values()),
            "expanded public category allocation is not exactly 260 by 128")
    return {
        "schema": SCHEMA, "python": "3.14.6", "cohort": "calibration",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "seed_domain": SEED_DOMAIN, "selection_seed": SELECTION_SEED,
        "order_seed_domain": ORDER_SEED_DOMAIN, "order_seed": ORDER_SEED,
        "bootstrap_seed_domain": BOOTSTRAP_SEED_DOMAIN,
        "bootstrap_seed": BOOTSTRAP_SEED,
        **program,
        "cases": CASE_COUNT, "original_cases_preserved": ORIGINAL_CASE_COUNT,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "cases_per_category": CASES_PER_CATEGORY,
        "public_operations": dict(sorted(operations.items())),
        "categories": dict(sorted(categories.items())),
        "semantic_identity_count": len(identities),
        "semantic_identity_sha256": digest(identities),
        "frozen_warmups": WARMUPS, "frozen_trials": PAIRED_TRIALS,
        "frozen_bootstrap_samples": BOOTSTRAP_DRAWS,
        "expected_raw_rows": CASE_COUNT * (len(CANDIDATES) + 1) * PAIRED_TRIALS,
        "expected_correctness_answers": CASE_COUNT * (len(CANDIDATES) + 1) * PAIRED_TRIALS * 3,
        "expected_confidence_intervals": (CASE_COUNT + 1) * len(CANDIDATES),
        "expected_process_native_checks": CASE_COUNT * 8 + 8,
        "baseline": BASELINE, "candidates": list(CANDIDATES),
        "maximum_subject_limit": SUBJECT_LIMIT, "maximum_result_limit": RESULT_LIMIT,
        "goal_sha256": PUBLIC_FILE_SHA256["GOAL.md"],
        "source_public_manifest": "performance/postfinal-public-v6/manifest.json",
        "source_public_manifest_sha256": PUBLIC_FILE_SHA256["performance/postfinal-public-v6/manifest.json"],
        "source_public_fixture": "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
        "source_public_fixture_sha256": PUBLIC_FILE_SHA256["performance/v7/evidence/rust-calibration-fixture.jsonl.gz"],
        "pinned_public_input_sha256": dict(sorted(PUBLIC_FILE_SHA256.items())),
        "qualified_source_fingerprints": provenance["sources"],
        "native_elf_fingerprints": provenance["native"],
        "stage10_correctness": provenance["stage10"],
        "independent_cpython_self_oracle": {"workers": 2, "schema": ORACLE_SCHEMA,
                                              "python": "3.14.6", "failed": 0},
        "selected_cases": descriptors, "case_records": complete,
        "candidate_imports": [], "historical_results_read": 0,
        "standalone_startup_cost": "NOT MEASURED",
        "standalone_ffi_cost": "NOT MEASURED",
        "inside_native_allocation": "NOT MEASURED",
        "timing_performed": False, "performance": "NOT MEASURED",
    }


def exclusive_manifest_write(manifest: dict[str, Any], program: dict[str, str],
                             provenance: dict[str, Any]) -> Path:
    require(public_program_fingerprints() == program,
            "public V8 generator or protocol changed before exclusive output")
    verify_live_owned_artifacts(provenance)
    require(all(manifest.get(key) == value for key, value in program.items()),
            "public V8 manifest does not bind its actual runner and protocol")
    path = ROOT / "performance/postfinal-public-v8/manifest.json"
    require(path.parent.is_dir(), "public V8 protocol directory is missing")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o644)
    except FileExistsError as error:
        raise PublicExpansionError("public V8 manifest already exists; overwrite is forbidden") from error
    except OSError as error:
        raise PublicExpansionError("cannot exclusively create the public V8 manifest") from error
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(json_bytes(manifest) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    return path


def freeze_public_development() -> None:
    """Explicit future-only operation: all provenance and oracle gates run first."""
    program = public_program_fingerprints()
    parent, fixture_manifest, provenance = verify_public_provenance()
    fixture = load_public_fixture(fixture_manifest)
    rows = select_public_cases(parent, fixture)
    answers = require_independent_cpython_answers(rows)
    fixture_by_id = fixture
    for row, answer in zip(rows, answers, strict=True):
        if not row["generated"]:
            continue
        source_expected = fixture_by_id[row["source_id"]]["expected"]["result"]
        api = row["case"]["api"]
        if api not in {"compile", "escape"}:
            require(answer["result"] == source_expected,
                    "pattern-comment variant changed its source category's observable matching semantics")
        elif api == "compile":
            require(isinstance(answer["result"], dict) and isinstance(source_expected, dict),
                    "compile reference answer changed shape")
            require({k: v for k, v in answer["result"].items() if k != "pattern"}
                    == {k: v for k, v in source_expected.items() if k != "pattern"},
                    "compile variant changed flags or capture semantics")
    require(public_program_fingerprints() == program,
            "public V8 generator or protocol changed during independent self-oracles")
    verify_live_owned_artifacts(provenance)
    manifest = build_manifest(parent, rows, answers, provenance, program)
    output = exclusive_manifest_write(manifest, program, provenance)
    print(json.dumps({"schema": SCHEMA, "status": "PASS", "cases": CASE_COUNT,
                      "categories": CATEGORY_COUNT, "cases_per_category": CASES_PER_CATEGORY,
                      "public_operations": manifest["public_operations"],
                      "manifest": str(output.relative_to(ROOT)),
                      "performance": "NOT MEASURED"}, sort_keys=True))


def synthetic_public_inputs() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    """Construct a full-sized, wholly invented fixture entirely in memory."""
    fixtures: dict[str, dict[str, Any]] = {}
    descriptors: list[dict[str, Any]] = []
    operations: collections.Counter[str] = collections.Counter()
    categories: collections.Counter[str] = collections.Counter()
    empty_digest = digest(None)
    for index in range(FIXTURE_CASE_COUNT):
        category_number = index % CATEGORY_COUNT
        category = f"synthetic-category-{category_number:03d}"
        api = PUBLIC_OPERATIONS[category_number % len(PUBLIC_OPERATIONS)]
        binary = category_number % 4 != 0
        pattern_text = f"synthetic-{index:05d}"
        pattern: Any = (
            {PACKING_MARKER: "bytes", "hex": pattern_text.encode("ascii").hex()}
            if binary else pattern_text
        )
        subject_text = f"public-synthetic-subject-{index:05d}"
        subject: Any = (
            {PACKING_MARKER: "bytes", "hex": subject_text.encode("ascii").hex()}
            if binary else subject_text
        )
        case: dict[str, Any] = {
            "id": f"cal.synthetic.public.{index:05d}",
            "cohort": "calibration", "category": category, "api": api,
            "lifecycle": "cold" if api == "compile" else "module" if api == "escape"
            else "compiled",
            "pattern": pattern,
            "string": None if api in {"compile", "escape"} else subject,
            "flags": ["X"] if index % 17 == 0 and api != "escape" else [],
            "ops": 1, "weight": 1,
        }
        if api not in {"compile", "escape"} and category_number % 4 == 2:
            case["subject_kind"] = "bytearray"
        elif api not in {"compile", "escape"} and category_number % 4 == 3:
            case["subject_kind"] = "memoryview"
        expected = {
            "id": case["id"], "cohort": "calibration", "category": category,
            "result": None, "result_sha256": empty_digest,
        }
        fixtures[case["id"]] = {
            "position": index, "case": case, "expected": expected,
        }
        if index < ORIGINAL_CASE_COUNT:
            operations[api] += 1
            categories[category] += 1
            descriptors.append({
                "api": api, "case": case["id"], "category": category,
                "cohort": "calibration", "expected_result_sha256": empty_digest,
                "frozen_operations": 1, "input": source_kind(case),
                "lifecycle": case["lifecycle"], "result_count": 0,
                "result_density": "none", "selection_reasons": ["synthetic"],
                "subject_length": len(unpack(subject))
                if case["string"] is not None else 0,
            })
    uncompressed = hashlib.sha256(b"synthetic-public-only").hexdigest()
    fixture_manifest = {
        "schema": FIXTURE_MANIFEST_SCHEMA, "python": "3.14.6",
        "cohort": "calibration", "cases": FIXTURE_CASE_COUNT,
        "fixture": "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
        "fixture_sha256": PUBLIC_FILE_SHA256[
            "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"],
        "uncompressed_fixture_sha256": uncompressed, "failed": 0,
    }
    parent = {
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v6",
        "python": "3.14.6", "cases": ORIGINAL_CASE_COUNT,
        "cohort": "calibration", "all_bounded_workload_categories": CATEGORY_COUNT,
        "public_operations": dict(operations), "categories": dict(categories),
        "selected_cases": descriptors,
        "source_fixture": fixture_manifest["fixture"],
        "source_fixture_sha256": fixture_manifest["fixture_sha256"],
        "source_fixture_manifest_sha256": PUBLIC_FILE_SHA256[
            "performance/v7/evidence/rust-calibration-fixture-manifest.json"],
        "source_fixture_uncompressed_sha256": uncompressed,
    }
    return parent, fixtures, fixture_manifest


def synthetic_qualification_inputs() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any],
    dict[str, str], dict[str, Any], dict[str, Any],
]:
    """Make invented V5/Stage10 evidence; read no actual report or source."""
    sources = {relative: hashlib.sha256(
        f"synthetic-source:{relative}".encode("ascii")
    ).hexdigest() for relative in sorted(REQUIRED_SOURCE_PATHS)}
    native = {role: hashlib.sha256(
        f"synthetic-native:{role}".encode("ascii")
    ).hexdigest() for role in sorted(REQUIRED_NATIVE_ROLES)}
    family_sources: dict[str, dict[str, str]] = {
        family: {} for family in sorted(REQUIRED_FAMILIES)
    }
    for relative, fingerprint in sources.items():
        if relative in {"candidates/_vm_native.c", "candidates/vm_candidate.py"}:
            family = "vm"
        elif relative.startswith("candidates/zig/") or relative == "candidates/zig_candidate.py":
            family = "zig"
        else:
            family = "rust"
        family_sources[family][relative] = fingerprint
    family_native: dict[str, dict[str, str]] = {}
    native_records: dict[str, dict[str, Any]] = {}
    for family, roles in NATIVE_RECORD_ROLES.items():
        family_native[family] = {
            REQUIRED_NATIVE_FILES[role]: native[role] for role in roles.values()
        }
        native_records[family] = {
            "passed": True, "issues": [],
            "files": {
                name: {"file": REQUIRED_NATIVE_FILES[role],
                       "sha256": native[role],
                       "forbidden_regex_symbols": [],
                       "cross_candidate_symbols": []}
                for name, role in roles.items()
            },
        }
    families = {family: {"passed": True} for family in REQUIRED_FAMILIES}
    base = {
        "postfinal_schema": "rebar-postfinal-from-scratch-audit-v5",
        "status": "PASS", "result": "PASS", "passed": True,
        "verified_core_family_count": 3, "families": families,
        "audit_source_path": "tools/postfinal_from_scratch_audit_v5.py",
        "audit_source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_from_scratch_audit_v5.py"],
        "self_test": {"passed": True, "check_count": 76, "failed": []},
        "postfinal_wrapper_self_test": {
            "passed": True, "status": "PASS", "check_count": 198,
            "failed": [],
        },
    }
    strict = {
        "schema": "rebar-postfinal-no-delegation-audit-v5",
        "status": "PASS", "result": "PASS", "passed": True,
        "verified_core_family_count": 3, "families": families,
        "audit_source_path": "tools/postfinal_no_delegation_audit_v5.py",
        "audit_source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_no_delegation_audit_v5.py"],
        "self_test": {"passed": True, "check_count": 32, "failed": []},
        "inherited_control_count": 76,
        "postfinal_wrapper_self_test": {
            "passed": True, "status": "PASS", "check_count": 676,
            "failed": [],
        },
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        "native_elf_provenance": {
            "passed": True, "issues": [], "audited_binary_count": 5,
            "expected_binary_count": 5, "families": native_records,
        },
    }
    method_names = ["ReTests.test_locale_compiled", "ReTests.test_locale_caching"]
    method_names.extend(f"SyntheticReTests.test_{index:03d}" for index in range(144))
    method_records = [{"test": name, "status": "passed", "skipped": 0}
                      for name in method_names]
    locale_roles = {
        family: {
            "module": "re" if family == "re" else f"candidates.{family}_candidate",
            "methods": 146, "passed": 146, "failed": 0, "errors": 0,
            "skipped": 0, "crashes": 0, "timeouts": 0,
            "locale_compiled_passed": True, "locale_caching_passed": True,
            "timing_performed": False, "performance": "NOT MEASURED",
            "records": method_records,
        }
        for family in ("re", "rust", "vm", "zig")
    }
    locale = {
        "schema": "rebar-postfinal-cpython-public-locale-v1",
        "python": "3.14.6", "status": "PASS", "result": "PASS",
        "goal_sha256": PUBLIC_FILE_SHA256["GOAL.md"],
        "source_path": "tools/postfinal_cpython_locale_oracle_v1.py",
        "source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_cpython_locale_oracle_v1.py"],
        "timing_performed": False, "performance": "NOT MEASURED",
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native, "roles": locale_roles,
    }
    stage06_audit = {
        "oracle_source_path": "tools/python_re_universal_public_oracle_stage06.py",
        "oracle_source_sha256": PUBLIC_FILE_SHA256[
            "tools/python_re_universal_public_oracle_stage06.py"],
        "guarded_worker_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "guarded_worker_source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_no_delegation_audit_v1.py"],
        "postfinal_audit_source_path": "tools/postfinal_from_scratch_audit_v5.py",
        "postfinal_audit_source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_from_scratch_audit_v5.py"],
        "postfinal_no_delegation_audit_source_path":
            "tools/postfinal_no_delegation_audit_v5.py",
        "postfinal_no_delegation_audit_source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_no_delegation_audit_v5.py"],
        "official_locale_source_path": "tools/postfinal_cpython_locale_oracle_v1.py",
        "official_locale_source_sha256": PUBLIC_FILE_SHA256[
            "tools/postfinal_cpython_locale_oracle_v1.py"],
        "selected_candidates": ["rust", "vm", "zig"],
        "previous_public_timing_evidence_read": False,
        "source_sha256": family_sources,
        "native_binary_sha256": family_native,
    }
    reports = {
        family: {"status": "PASS", "mismatches": 0,
                 "case_sha256": UNIVERSAL_CASE_SHA256,
                 "cases": ORIGINAL_CASE_COUNT,
                 "benchmark_or_timing_executed": False,
                 "performance_fixtures_read": 0}
        for family in REQUIRED_FAMILIES
    }
    universal = {
        "schema": "rebar-python-re-universal-public-oracle-v1",
        "python": "3.14.6", "status": "PASS", "comparison_complete": True,
        "mismatches": 0, "cases": ORIGINAL_CASE_COUNT,
        "case_sha256": UNIVERSAL_CASE_SHA256,
        "completed_candidates": ["rust", "vm", "zig"],
        "selected_candidates": ["rust", "vm", "zig"],
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED", "performance_fixtures_read": 0,
        "external_regex_packages": 0, "observations_per_case": 48,
        "observations_per_candidate": 393_216,
        "total_comparisons": 1_179_648,
        "planned_total_comparisons": 1_179_648,
        "candidate_reports": reports, "audit": stage06_audit,
    }
    pins = {
        relative: hashlib.sha256(
            f"synthetic-stage10:{relative}".encode("ascii")
        ).hexdigest()
        for relative in STAGE10_PINNED_SHA256
    }
    reference_records = [
        {"id": f"{cohort}:{index:04d}", "cohort": cohort,
         "status": "synthetic",
         "value": "\ud800" if cohort == "bounded-unicode"
         and index % 16 == 10 else "\udfff"
         if cohort == "bounded-unicode" and index % 16 == 11
         else f"synthetic-{cohort}-{index:04d}"}
        for cohort, count in STAGE10_COHORT_CASES.items()
        for index in range(count)
    ]
    record_hash = digest(reference_records)
    stage_provenance = {
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "observation_domain": STAGE10_OBSERVATION_DOMAIN,
        "official_methods_per_role": 146,
        "official_role_count": 4, "official_skipped": 0,
        "source_sha256_by_family": family_sources,
        "native_sha256_by_family": family_native,
        "previous_failed_source_path":
            "tools/python_re_universal_public_oracle_stage07.py",
        "previous_failed_source_sha256": PUBLIC_FILE_SHA256[
            "tools/python_re_universal_public_oracle_stage07.py"],
        "previous_failed_protocol_path":
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md",
        "previous_failed_protocol_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md"],
        "previous_self_oracle_failure_path":
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v7-self-oracle-failures.json",
        "previous_self_oracle_failure_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v7-self-oracle-failures.json"],
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
        "previous_stage08_source_path":
            "tools/python_re_universal_public_oracle_stage08.py",
        "previous_stage08_source_sha256": PUBLIC_FILE_SHA256[
            "tools/python_re_universal_public_oracle_stage08.py"],
        "previous_stage08_protocol_path":
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md",
        "previous_stage08_protocol_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md"],
        "previous_stage08_self_oracle_path":
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v8-self-oracle.json",
        "previous_stage08_self_oracle_sha256": PUBLIC_FILE_SHA256[
            "oracle/cpython-3.14.6/evidence/"
            "public-contract-v8-self-oracle.json"],
        "previous_stage08_rust_failure_path":
            "candidates/evidence/"
            "python-re-universal-public-oracle-v8-rust-failures.json",
        "previous_stage08_rust_failure_sha256": PUBLIC_FILE_SHA256[
            "candidates/evidence/"
            "python-re-universal-public-oracle-v8-rust-failures.json"],
        "previous_stage08_rust_failure_count": 256,
        "previous_stage08_rust_matching_observations": 3_328,
        "previous_stage08_rust_failure_preserved": True,
    }
    stage_reference = {
        "schema": STAGE10_SELF_ORACLE_SCHEMA, "status": "PASS",
        "result": "PASS", "python": "3.14.6",
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "seed": STAGE10_SEED, "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": STAGE10_COHORTS,
        "cohort_cases": dict(STAGE10_COHORT_CASES),
        "cases": STAGE10_CASES,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "stdlib_checks": STAGE10_CASES * 2,
        "baseline_record_sha256": record_hash,
        "second_record_sha256": record_hash,
        "baseline_records": reference_records,
        "mismatches": 0, "failure_records": [],
        "current_provenance": stage_provenance,
        "locales": {"synthetic-locale": "C"},
        "candidate_imports": 0, "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    candidate_reports: dict[str, Any] = {}
    for family, roles in NATIVE_RECORD_ROLES.items():
        expected_native = {
            REQUIRED_NATIVE_FILES[role]: native[role]
            for role in roles.values()
        }
        candidate_reports[family] = {
            "candidate": family, "module": f"candidates.{family}_candidate",
            "status": "PASS", "cases": STAGE10_CASES,
            "cohort_cases": dict(STAGE10_COHORT_CASES), "mismatches": 0,
            "failure_records": [], "failures_recorded": 0,
            "native_binary_sha256": expected_native,
            "guard": {
                "enabled": True, "family": family,
                "stdlib_re_blocked": True, "cpython_sre_blocked": True,
                "third_party_regex_blocked": True,
                "cross_family_blocked": True,
                "foreign_dynamic_libraries_blocked": True,
                "cached_regex_aliases_poisoned": 10,
                "native_loader_aliases_blocked":
                    list(STAGE10_NATIVE_LOADER_ALIASES),
                "loaded_candidate_modules": {
                    "rust": ["candidates._rust_bridge",
                             "candidates.rust_candidate"],
                    "vm": ["candidates._vm_native",
                           "candidates.vm_candidate"],
                    "zig": ["candidates._zig_bridge",
                            "candidates.zig_candidate"],
                }[family],
                "prohibited_modules": sorted(
                    {"re", "_sre", "regex", "re2", "pcre", "pcre2"}
                    | {f"candidates.{peer}_candidate"
                       for peer in REQUIRED_FAMILIES if peer != family}
                ),
                "isolated_public_metadata": {
                    "enabled": True,
                    "schema": STAGE10_METADATA_SCHEMA,
                    "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
                    "role": family,
                    "surface_cases": 256,
                    "record_sha256": hashlib.sha256(
                        f"synthetic-stage10-metadata:{family}".encode("ascii")
                    ).hexdigest(),
                    "production_matching_executed": False,
                    "metadata_and_matcher_processes_distinct": True,
                    "matcher_inspect_loaded": False,
                    "matcher_tokenizer_loaded": False,
                },
            },
            "benchmark_or_timing_executed": False,
            "holdout_cases_read": 0, "performance": "NOT MEASURED",
        }
    stage_all = {
        "schema": STAGE10_ALL_CANDIDATES_SCHEMA,
        "status": "PASS", "result": "PASS", "selected": "all",
        "selected_candidates": ["rust", "vm", "zig"],
        "completed_candidates": ["rust", "vm", "zig"],
        "comparison_complete": True, "python": "3.14.6",
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": pins[STAGE10_SOURCE_RELATIVE],
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": pins[STAGE10_PROTOCOL_RELATIVE],
        "seed": STAGE10_SEED, "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": STAGE10_COHORTS,
        "cohort_cases": dict(STAGE10_COHORT_CASES),
        "cases_per_candidate": STAGE10_CASES,
        "candidate_checks": STAGE10_CASES * len(REQUIRED_FAMILIES),
        "previous_public_cases": ORIGINAL_CASE_COUNT,
        "previous_public_comparisons": 1_179_648,
        "combined_public_comparisons": 1_190_400,
        "mismatches": 0, "self_oracle_path": STAGE10_SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": pins[STAGE10_SELF_ORACLE_RELATIVE],
        "current_provenance": stage_provenance,
        "locales": stage_reference["locales"],
        "candidate_reports": candidate_reports,
        "external_regex_packages": 0, "candidate_cross_delegation": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0, "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    return base, strict, locale, universal, pins, stage_reference, stage_all


def self_test() -> None:
    """Exercise only synthetic values in memory; do not touch files or processes."""
    checks: list[str] = []
    before_candidates = {name for name in sys.modules if name == "candidates" or name.startswith("candidates.")}
    blocked_attempts: collections.Counter[str] = collections.Counter()
    original_subprocess_run = subprocess.run
    original_gzip_open = gzip.open
    original_path_open = Path.open
    original_os_open = os.open
    clock_names = (
        "time", "time_ns", "monotonic", "monotonic_ns",
        "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
    )
    original_clocks = {name: getattr(time, name) for name in clock_names}

    def deny_subprocess(*_args: Any, **_kwargs: Any) -> Any:
        blocked_attempts["subprocess"] += 1
        raise PublicExpansionError("synthetic self-test cannot start a subprocess")

    def deny_gzip(*_args: Any, **_kwargs: Any) -> Any:
        blocked_attempts["compressed-fixture"] += 1
        raise PublicExpansionError("synthetic self-test cannot open a compressed fixture")

    def deny_path(*_args: Any, **_kwargs: Any) -> Any:
        blocked_attempts["path"] += 1
        raise PublicExpansionError("synthetic self-test cannot open a filesystem path")

    def deny_os_open(*_args: Any, **_kwargs: Any) -> Any:
        blocked_attempts["output"] += 1
        raise PublicExpansionError("synthetic self-test cannot create a manifest")

    def deny_clock(*_args: Any, **_kwargs: Any) -> Any:
        blocked_attempts["clock"] += 1
        raise PublicExpansionError("synthetic self-test cannot sample a clock")

    subprocess.run = deny_subprocess  # type: ignore[assignment]
    gzip.open = deny_gzip  # type: ignore[assignment]
    Path.open = deny_path  # type: ignore[assignment]
    os.open = deny_os_open  # type: ignore[assignment]
    for clock_name in clock_names:
        setattr(time, clock_name, deny_clock)

    def check(label: str, value: object) -> None:
        require(label not in checks, f"duplicate synthetic control: {label}")
        require(value, f"synthetic public expansion control failed: {label}")
        checks.append(label)

    def rejected(label: str, function: Any) -> None:
        try:
            function()
        except PublicExpansionError:
            check(label, True)
        else:
            raise PublicExpansionError(f"synthetic poison was accepted: {label}")

    check("public-domain-is-separated", SEED_DOMAIN == "rebar/public-development/v8")
    check("selection-seed-is-exact", SELECTION_SEED == 2026072428)
    check("paired-order-seed-is-exact", ORDER_SEED == 2026072429)
    check("bootstrap-seed-is-exact", BOOTSTRAP_SEED == 2026072430)
    check("all-three-seeds-are-distinct",
          len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3)
    check("paired-order-domain-is-separated",
          ORDER_SEED_DOMAIN == "rebar/public-development/v8/paired-order")
    check("bootstrap-domain-is-separated",
          BOOTSTRAP_SEED_DOMAIN == "rebar/public-development/v8/bootstrap")
    check("all-three-seed-domains-are-distinct",
          len({SEED_DOMAIN, ORDER_SEED_DOMAIN, BOOTSTRAP_SEED_DOMAIN}) == 3)
    check("deterministic-public-seed", seed_key("synthetic") == seed_key("synthetic"))
    check("changed-domain-changes-selection", seed_key("synthetic") != seed_key("synthetic", domain="rebar/public-development/not-v8"))
    check("changed-seed-changes-selection", seed_key("synthetic") != seed_key("synthetic", seed=SELECTION_SEED + 1))
    check("bytes-and-text-do-not-collide", canonical(b"abc") != canonical("abc"))
    check("bytes-and-bytearray-do-not-collide", canonical(b"abc") != canonical(bytearray(b"abc")))
    check("bytes-and-memoryview-do-not-collide", canonical(b"abc") != canonical(memoryview(b"abc")))
    check("tuple-and-list-do-not-collide", canonical((1, 2)) != canonical([1, 2]))
    check("boolean-and-integer-do-not-collide", canonical(True) != canonical(1))
    check("dict-order-is-canonical", canonical({"a": 1, "b": 2}) == canonical({"b": 2, "a": 1}))
    check("lone-surrogate-is-preserved", canonical("\ud800") != canonical("\ufffd"))
    check("packed-bytes-retain-type", canonical({PACKING_MARKER: "bytes", "hex": "6162"}) == canonical(b"ab"))
    check("packed-bytearray-retains-type", canonical({PACKING_MARKER: "bytearray", "hex": "6162"}) != canonical(b"ab"))
    rejected("invalid-packed-byte-hex-rejected", lambda: canonical({PACKING_MARKER: "bytes", "hex": "no"}))
    rejected("unknown-packed-type-rejected", lambda: canonical({PACKING_MARKER: "foreign", "hex": "61"}))
    rejected("reserved-packed-extra-field-rejected", lambda: canonical({PACKING_MARKER: "bytes", "hex": "61", "extra": 1}))
    rejected("unsupported-floating-identity-rejected", lambda: canonical(1.0))
    base = {"api": "search", "category": "synthetic-search", "cohort": "calibration",
            "lifecycle": "compiled", "pattern": "needle", "string": "a needle b",
            "flags": [], "id": "cal.synthetic.search", "ops": 1, "weight": 1}
    reference = {"position": 0, "case": base,
                 "expected": {"id": base["id"], "cohort": "calibration",
                              "category": base["category"], "result": None,
                              "result_sha256": digest(None)}}
    variant = make_variant(reference, 0)
    check("variation-preserves-public-cohort", variant["cohort"] == "calibration")
    check("variation-preserves-category", variant["category"] == base["category"])
    check("variation-preserves-operation", variant["api"] == base["api"])
    check("variation-preserves-lifecycle", variant["lifecycle"] == base["lifecycle"])
    check("variation-preserves-flags", variant["flags"] == base["flags"])
    check("variation-preserves-exact-subject", variant["string"] == base["string"])
    check("variation-changes-semantic-identity", semantic_identity(variant) != semantic_identity(base))
    check("variation-is-reproducible", make_variant(reference, 0) == variant)
    check("distinct-variation-has-distinct-identity", semantic_identity(make_variant(reference, 1)) != semantic_identity(variant))
    check("pattern-comment-is-fixed-width", len(make_variant(reference, 0)["pattern"]) == len(make_variant(reference, 1)["pattern"]))
    byte_pattern = {PACKING_MARKER: "bytes", "hex": "616263"}
    check("binary-comment-remains-bytes", unpack(append_public_pattern(byte_pattern, "(?#r8-x)")) == b"abc(?#r8-x)")
    rejected("mutable-pattern-rejected", lambda: append_public_pattern({PACKING_MARKER: "bytearray", "hex": "61"}, "(?#x)"))
    rejected("non-ascii-comment-rejected", lambda: append_public_pattern("a", "\u00e9"))
    rejected("negative-variant-rejected", lambda: make_variant(reference, -1))
    rejected("boolean-variant-rejected", lambda: make_variant(reference, True))
    altered_argument = dict(base, pos=1)
    check("pos-participates-in-identity", semantic_identity(altered_argument) != semantic_identity(base))
    check("flags-participate-in-identity", semantic_identity(dict(base, flags=["I"])) != semantic_identity(base))
    check("lifecycle-participates-in-identity", semantic_identity(dict(base, lifecycle="module")) != semantic_identity(base))
    check("subject-participates-in-identity", semantic_identity(dict(base, string="other")) != semantic_identity(base))
    check("operation-participates-in-identity", semantic_identity(dict(base, api="match")) != semantic_identity(base))
    typed_binary = dict(base, pattern={PACKING_MARKER: "bytes", "hex": "61"},
                        string={PACKING_MARKER: "bytes", "hex": "6162"})
    check("declared-bytearray-participates-in-identity",
          semantic_identity(dict(typed_binary, subject_kind="bytearray"))
          != semantic_identity(dict(typed_binary, subject_kind="bytes")))
    check("declared-memoryview-participates-in-identity",
          semantic_identity(dict(typed_binary, subject_kind="memoryview"))
          != semantic_identity(dict(typed_binary, subject_kind="bytearray")))
    check("source-kind-retains-bytearray",
          source_kind(dict(typed_binary, subject_kind="bytearray")) == "bytearray")
    check("source-kind-retains-memoryview",
          source_kind(dict(typed_binary, subject_kind="memoryview")) == "memoryview")
    check("effective-bytearray-retains-owned-buffer",
          isinstance(effective_subject(dict(typed_binary, subject_kind="bytearray")),
                     bytearray))
    check("effective-memoryview-retains-owned-buffer",
          isinstance(effective_subject(dict(typed_binary, subject_kind="memoryview")),
                     memoryview))
    escape_binary = dict(typed_binary, api="escape", string=None,
                         id="cal.synthetic.escape", category="synthetic-escape",
                         lifecycle="module")
    escape_reference = {"case": escape_binary}
    escape_variant = make_variant(escape_reference, 0)
    check("binary-escape-retains-exact-bytes-input",
          source_kind(escape_variant) == "bytes"
          and isinstance(unpack(escape_variant["pattern"]), bytes))
    check("binary-escape-uses-literal-not-regex-comment",
          b"-r8-" in unpack(escape_variant["pattern"])
          and b"(?#" not in unpack(escape_variant["pattern"]))
    rejected("missing-semantic-pattern-rejected", lambda: semantic_identity({k: v for k, v in base.items() if k != "pattern"}))
    opaque = {"case": base, "cohort": "calibration", "expected": reference["expected"],
              "historical": {"poison": [{"opaque": "do-not-decode"}]}, "position": 0,
              "schema": FIXTURE_SCHEMA}
    encoded = json_bytes(opaque) + b"\n"
    poison_offset = encoded.decode("utf-8").index('"historical"')
    poison_end = encoded.decode("utf-8").index('"position"')

    class PublicOnlyDecoder:
        def __init__(self) -> None:
            self.inner = json.JSONDecoder()

        def raw_decode(self, text: str, index: int = 0) -> tuple[Any, int]:
            require(not (poison_offset < index < poison_end), "opaque history reached JSON deserialization")
            return self.inner.raw_decode(text, index)

    decoded = decode_public_fixture_line(encoded, PublicOnlyDecoder())
    check("opaque-history-is-never-deserialized", "historical" not in decoded and decoded["case"] == base)
    check("public-fixture-schema-survives-selective-decoding", decoded["schema"] == FIXTURE_SCHEMA)
    rejected("unexpected-fixture-field-rejected", lambda: decode_public_fixture_line(json_bytes(dict(opaque, foreign=True))))
    rejected("truncated-fixture-field-rejected", lambda: decode_public_fixture_line(b'{"case":'))
    check("published-stage10-pins-are-complete",
          validate_stage10_pinset(STAGE10_PINNED_SHA256)
          == STAGE10_PINNED_SHA256)

    synthetic_base, synthetic_strict, synthetic_locale, synthetic_universal, synthetic_pins, \
        synthetic_stage_reference, synthetic_stage_all = synthetic_qualification_inputs()
    check("complete-synthetic-stage10-pins-validate",
          validate_stage10_pinset(synthetic_pins) == synthetic_pins)
    for relative in sorted(synthetic_pins):
        incomplete = dict(synthetic_pins)
        incomplete[relative] = None
        label = relative.rsplit("/", 1)[-1].replace(".", "-")
        rejected(f"unpublished-stage10-{label}-rejected",
                 lambda values=incomplete: validate_stage10_pinset(values))
    omitted_pin = dict(synthetic_pins)
    omitted_pin.pop(STAGE10_SELF_ORACLE_RELATIVE)
    rejected("omitted-stage10-reference-pin-rejected",
             lambda: validate_stage10_pinset(omitted_pin))
    extra_pin = dict(synthetic_pins)
    extra_pin["synthetic/unapproved.json"] = "a" * 64
    rejected("unapproved-stage10-proof-path-rejected",
             lambda: validate_stage10_pinset(extra_pin))
    invalid_pin = dict(synthetic_pins)
    invalid_pin[STAGE10_SOURCE_RELATIVE] = "not-a-sha256"
    rejected("invalid-stage10-source-hash-rejected",
             lambda: validate_stage10_pinset(invalid_pin))
    synthetic_provenance = validate_candidate_proofs(
        synthetic_base, synthetic_strict, synthetic_locale, synthetic_universal)
    check("synthetic-v5-proves-twelve-current-sources",
          len(synthetic_provenance["sources"]) == 12)
    check("synthetic-v5-proves-five-native-roles",
          len(synthetic_provenance["native"]) == 5)
    stage_evidence = validate_stage10_documents(
        synthetic_stage_reference, synthetic_stage_all,
        synthetic_pins, synthetic_provenance)
    synthetic_provenance["stage10"] = stage_evidence
    check("synthetic-stage10-dual-reference-is-qualified",
          stage_evidence["stdlib_checks"] == 7_168)
    check("synthetic-stage10-three-families-are-qualified",
          stage_evidence["candidate_checks"] == 10_752)
    check("synthetic-stage10-exact-eight-cohorts-are-qualified",
          STAGE10_COHORT_CASES == synthetic_stage_reference["cohort_cases"]
          and sum(STAGE10_COHORT_CASES.values()) == 3_584)
    check("synthetic-stage10-preserves-lone-unicode-surrogates",
          any(record.get("value") == "\ud800"
              for record in synthetic_stage_reference["baseline_records"])
          and any(record.get("value") == "\udfff"
                  for record in synthetic_stage_reference["baseline_records"]))
    check("synthetic-stage10-surrogate-digest-is-reproducible",
          digest(synthetic_stage_reference["baseline_records"])
          == synthetic_stage_reference["baseline_record_sha256"])
    check("synthetic-stage10-preserves-real-prior-failures",
          synthetic_stage_reference["current_provenance"]
          ["previous_self_oracle_failure_count"] == 32
          and synthetic_stage_reference["current_provenance"]
          ["previous_stage08_rust_failure_count"] == 256)

    def stage_reject(label: str, *, reference_change: dict[str, Any] | None = None,
                     all_change: dict[str, Any] | None = None) -> None:
        reference_value = dict(synthetic_stage_reference)
        all_value = dict(synthetic_stage_all)
        if reference_change:
            reference_value.update(reference_change)
        if all_change:
            all_value.update(all_change)
        rejected(label, lambda: validate_stage10_documents(
            reference_value, all_value, synthetic_pins, synthetic_provenance))

    stage_reject("wrong-stage10-reference-schema-rejected",
                 reference_change={"schema": "synthetic-wrong-schema"})
    stage_reject("wrong-stage10-matrix-rejected",
                 reference_change={"matrix_sha256": "0" * 64})
    stage_reject("wrong-stage10-reference-seed-rejected",
                 reference_change={"seed": STAGE10_SEED + 1})
    stage_reject("wrong-stage10-reference-domain-rejected",
                 reference_change={"seed_domain": "synthetic-other-domain"})
    stage_reject("wrong-stage10-reference-count-rejected",
                 reference_change={"cases": STAGE10_CASES - 1})
    stage_reject("wrong-stage10-dual-reference-count-rejected",
                 reference_change={"stdlib_checks": 7_167})
    stage_reject("missing-independent-stage10-reference-rejected",
                 reference_change={"independent_stdlib_roles": ["stdlib-a"]})
    stage_reject("disagreeing-independent-stage10-reference-rejected",
                 reference_change={"second_record_sha256": "0" * 64})
    wrong_cohorts = dict(STAGE10_COHORT_CASES)
    wrong_cohorts["public-surface"] -= 1
    wrong_cohorts["invalid-grammar"] += 1
    stage_reject("silently-reweighted-stage10-cohort-rejected",
                 reference_change={"cohort_cases": wrong_cohorts})
    wrong_records = list(synthetic_stage_reference["baseline_records"])
    wrong_records[0], wrong_records[1] = wrong_records[1], wrong_records[0]
    stage_reject("reordered-stage10-obligation-identities-rejected",
                 reference_change={"baseline_records": wrong_records,
                                   "baseline_record_sha256": digest(wrong_records),
                                   "second_record_sha256": digest(wrong_records)})
    stage_reject("wrong-stage10-all-family-schema-rejected",
                 all_change={"schema": "synthetic-wrong-all-schema"})
    stage_reject("wrong-stage10-candidate-count-rejected",
                 all_change={"candidate_checks": 10_751})
    stage_reject("wrong-stage10-combined-denominator-rejected",
                 all_change={"combined_public_comparisons": 1_190_399})
    stage_reject("stage10-candidate-mismatch-rejected",
                 all_change={"mismatches": 1})
    stage_reject("stage10-self-proof-digest-substitution-rejected",
                 all_change={"self_oracle_sha256": "0" * 64})
    stage_reject("stage10-external-package-rejected",
                 all_change={"external_regex_packages": 1})
    stage_reject("stage10-cross-family-delegation-rejected",
                 all_change={"candidate_cross_delegation": True})
    stage_reject("stage10-timing-contamination-rejected",
                 all_change={"benchmark_or_timing_executed": True})
    missing_family = dict(synthetic_stage_all["candidate_reports"])
    missing_family.pop("zig")
    stage_reject("missing-stage10-zig-family-rejected",
                 all_change={"candidate_reports": missing_family})
    bad_family = dict(synthetic_stage_all["candidate_reports"])
    bad_rust = dict(bad_family["rust"])
    bad_guard = dict(bad_rust["guard"])
    bad_guard["stdlib_re_blocked"] = False
    bad_rust["guard"] = bad_guard
    bad_family["rust"] = bad_rust
    stage_reject("stage10-stdlib-delegation-guard-rejected",
                 all_change={"candidate_reports": bad_family})

    def candidate_guard_reject(label: str, family: str,
                               *, guard_change: dict[str, Any] | None = None,
                               metadata_change: dict[str, Any] | None = None,
                               ) -> None:
        reports = dict(synthetic_stage_all["candidate_reports"])
        entry = dict(reports[family])
        guard = dict(entry["guard"])
        if guard_change:
            guard.update(guard_change)
        if metadata_change:
            metadata = dict(guard["isolated_public_metadata"])
            metadata.update(metadata_change)
            guard["isolated_public_metadata"] = metadata
        entry["guard"] = guard
        reports[family] = entry
        stage_reject(label, all_change={"candidate_reports": reports})

    for alias in STAGE10_NATIVE_LOADER_ALIASES:
        fewer_aliases = [item for item in STAGE10_NATIVE_LOADER_ALIASES
                         if item != alias]
        label = alias.replace(".", "-")
        candidate_guard_reject(
            f"stage10-{label}-native-bypass-rejected", "rust",
            guard_change={"native_loader_aliases_blocked": fewer_aliases},
        )
    candidate_guard_reject(
        "stage10-cached-regex-alias-bypass-rejected", "rust",
        guard_change={"cached_regex_aliases_poisoned": 9},
    )
    candidate_guard_reject(
        "stage10-matcher-inspect-import-rejected", "rust",
        metadata_change={"matcher_inspect_loaded": True},
    )
    candidate_guard_reject(
        "stage10-matcher-tokenizer-import-rejected", "vm",
        metadata_change={"matcher_tokenizer_loaded": True},
    )
    candidate_guard_reject(
        "stage10-shared-metadata-matching-process-rejected", "zig",
        metadata_change={"metadata_and_matcher_processes_distinct": False},
    )
    candidate_guard_reject(
        "stage10-metadata-production-matching-rejected", "zig",
        metadata_change={"production_matching_executed": True},
    )
    candidate_guard_reject(
        "stage10-wrong-metadata-source-rejected", "rust",
        metadata_change={"source_sha256": "0" * 64},
    )
    candidate_guard_reject(
        "stage10-wrong-metadata-role-rejected", "vm",
        metadata_change={"role": "rust"},
    )
    candidate_guard_reject(
        "stage10-missing-public-metadata-surface-rejected", "zig",
        metadata_change={"surface_cases": 255},
    )
    candidate_guard_reject(
        "stage10-foreign-loaded-candidate-rejected", "rust",
        guard_change={"loaded_candidate_modules":
                      ["candidates.rust_candidate", "candidates.zig_candidate"]},
    )

    def history_reject(label: str, field: str, value: Any) -> None:
        changed = dict(synthetic_stage_reference["current_provenance"])
        changed[field] = value
        stage_reject(label, reference_change={"current_provenance": changed},
                     all_change={"current_provenance": changed})

    history_reject("stage10-concealed-python-self-failure-rejected",
                   "previous_self_oracle_failure_count", 0)
    history_reject("stage10-changed-python-self-failure-hash-rejected",
                   "previous_self_oracle_failure_sha256", "0" * 64)
    history_reject("stage10-concealed-rust-harness-failure-rejected",
                   "previous_stage08_rust_failure_count", 0)
    history_reject("stage10-changed-rust-harness-failure-hash-rejected",
                   "previous_stage08_rust_failure_sha256", "0" * 64)
    history_reject("stage10-denied-rust-harness-preservation-rejected",
                   "previous_stage08_rust_failure_preserved", False)
    history_reject("stage10-substitute-metadata-domain-rejected",
                   "observation_domain", "rebar/python-re/public-contract/other")

    synthetic_parent, synthetic_fixture, synthetic_fixture_manifest = synthetic_public_inputs()
    validate_public_source_documents(synthetic_parent, synthetic_fixture_manifest)
    check("synthetic-public-manifest-has-all-twelve-operations",
          set(synthetic_parent["public_operations"]) == set(PUBLIC_OPERATIONS))
    rows = select_public_cases(synthetic_parent, synthetic_fixture)
    check("synthetic-public-fixture-has-exact-10312-sources",
          len(synthetic_fixture) == FIXTURE_CASE_COUNT)
    check("synthetic-selection-has-exact-33280-cases",
          len(rows) == CASE_COUNT)
    check("synthetic-selection-preserves-original-8192-order",
          [row["case"]["id"] for row in rows[:ORIGINAL_CASE_COUNT]]
          == [entry["case"] for entry in synthetic_parent["selected_cases"]])
    selected_counts = collections.Counter(row["case"]["category"] for row in rows)
    check("synthetic-selection-has-exact-260-categories",
          len(selected_counts) == CATEGORY_COUNT)
    check("synthetic-selection-has-exact-128-per-category",
          all(count == CASES_PER_CATEGORY for count in selected_counts.values()))
    check("synthetic-selection-preserves-all-twelve-operations",
          {row["case"]["api"] for row in rows} == set(PUBLIC_OPERATIONS))
    check("synthetic-selection-identities-are-all-unique",
          len({semantic_identity(row["case"]) for row in rows}) == CASE_COUNT)
    answers = [{"id": row["case"]["id"], "result": None,
                "result_sha256": digest(None)} for row in rows]
    synthetic_program = {
        "runner_path": "tools/postfinal_public_expansion_v8.py",
        "runner_sha256": hashlib.sha256(b"synthetic-public-runner").hexdigest(),
        "protocol_path": "performance/postfinal-public-v8/PROTOCOL.md",
        "protocol_sha256": hashlib.sha256(b"synthetic-public-protocol").hexdigest(),
    }
    manifest = build_manifest(synthetic_parent, rows, answers,
                              synthetic_provenance, synthetic_program)
    check("synthetic-manifest-preserves-byte-exact-original-descriptors",
          json_bytes(manifest["selected_cases"][:ORIGINAL_CASE_COUNT])
          == json_bytes(synthetic_parent["selected_cases"]))
    check("synthetic-manifest-publishes-all-33280-identities",
          manifest["semantic_identity_count"] == CASE_COUNT
          and len(manifest["case_records"]) == CASE_COUNT)
    check("synthetic-manifest-identity-digest-is-reproducible",
          manifest["semantic_identity_sha256"]
          == digest([item["semantic_identity"]
                     for item in manifest["case_records"]]))
    check("synthetic-manifest-observed-api-denominators-sum-exactly",
          set(manifest["public_operations"]) == set(PUBLIC_OPERATIONS)
          and sum(manifest["public_operations"].values()) == CASE_COUNT)
    check("synthetic-manifest-preserves-all-four-input-types",
          {item["input"] for item in manifest["selected_cases"]}
          == {"text", "bytes", "bytearray", "memoryview"})
    check("synthetic-manifest-binds-exact-runner-protocol",
          all(manifest.get(key) == value
              for key, value in synthetic_program.items()))
    check("synthetic-manifest-binds-exact-three-seeds",
          (manifest["selection_seed"], manifest["order_seed"],
           manifest["bootstrap_seed"])
          == (2026072428, 2026072429, 2026072430))
    check("synthetic-manifest-binds-stage10-matrix",
          manifest["stage10_correctness"]["matrix_sha256"]
          == STAGE10_MATRIX_SHA256)
    check("synthetic-manifest-claims-no-ffi-breakout",
          manifest["standalone_ffi_cost"] == "NOT MEASURED")
    check("synthetic-manifest-claims-no-isolated-startup",
          manifest["standalone_startup_cost"] == "NOT MEASURED")
    check("synthetic-manifest-claims-no-native-allocation",
          manifest["inside_native_allocation"] == "NOT MEASURED")
    check("synthetic-manifest-claims-no-performance",
          manifest["performance"] == "NOT MEASURED"
          and manifest["timing_performed"] is False)
    missing_runner = dict(synthetic_program)
    missing_runner.pop("runner_sha256")
    rejected("manifest-missing-generator-hash-rejected",
             lambda: build_manifest(synthetic_parent, rows, answers,
                                    synthetic_provenance, missing_runner))
    changed_protocol = dict(synthetic_program,
                            protocol_path="synthetic/unapproved.md")
    rejected("manifest-substitute-protocol-rejected",
             lambda: build_manifest(synthetic_parent, rows, answers,
                                    synthetic_provenance, changed_protocol))
    rejected("manifest-short-answer-denominator-rejected",
             lambda: build_manifest(synthetic_parent, rows, answers[:-1],
                                    synthetic_provenance, synthetic_program))

    broken_base = dict(synthetic_base,
                       self_test={"passed": True, "check_count": 75,
                                  "failed": []})
    rejected("stale-from-scratch-control-count-rejected",
             lambda: validate_candidate_proofs(
                 broken_base, synthetic_strict, synthetic_locale,
                 synthetic_universal))
    broken_strict = dict(synthetic_strict, inherited_control_count=75)
    rejected("stale-inherited-no-delegation-controls-rejected",
             lambda: validate_candidate_proofs(
                 synthetic_base, broken_strict, synthetic_locale,
                 synthetic_universal))
    broken_wrapper = dict(synthetic_strict,
                          postfinal_wrapper_self_test={
                              "passed": True, "status": "PASS",
                              "check_count": 675, "failed": [],
                          })
    rejected("stale-no-delegation-wrapper-controls-rejected",
             lambda: validate_candidate_proofs(
                 synthetic_base, broken_wrapper, synthetic_locale,
                 synthetic_universal))
    changed_native = dict(synthetic_strict["native_elf_fingerprints"])
    changed_native["candidates.zig_candidate:native-engine"] = "0" * 64
    rejected("mixed-current-zig-native-proof-rejected",
             lambda: validate_candidate_proofs(
                 synthetic_base,
                 dict(synthetic_strict, native_elf_fingerprints=changed_native),
                 synthetic_locale, synthetic_universal))
    incomplete_sources = dict(synthetic_strict["qualified_source_fingerprints"])
    incomplete_sources.pop("candidates/zig/mini_regex.zig")
    rejected("missing-owned-zig-source-rejected",
             lambda: validate_candidate_proofs(
                 synthetic_base,
                 dict(synthetic_strict,
                      qualified_source_fingerprints=incomplete_sources),
                 synthetic_locale, synthetic_universal))
    rejected("wrong-immutable-goal-proof-rejected",
             lambda: validate_candidate_proofs(
                 synthetic_base, synthetic_strict,
                 dict(synthetic_locale, goal_sha256="0" * 64),
                 synthetic_universal))
    rejected("incomplete-public-stage06-proof-rejected",
             lambda: validate_candidate_proofs(
                 synthetic_base, synthetic_strict, synthetic_locale,
                 dict(synthetic_universal, mismatches=1)))

    rejected("synthetic-self-test-blocks-real-subprocess",
             lambda: subprocess.run(["synthetic-forbidden"]))
    rejected("synthetic-self-test-blocks-real-compressed-fixture",
             lambda: gzip.open("synthetic-forbidden.gz", "rb"))
    rejected("synthetic-self-test-blocks-real-path-read",
             lambda: Path("synthetic-forbidden").open("rb"))
    rejected("synthetic-self-test-blocks-real-output",
             lambda: os.open("synthetic-forbidden", os.O_CREAT))
    for clock_name in clock_names:
        rejected(f"synthetic-self-test-blocks-{clock_name}-clock",
                 lambda name=clock_name: getattr(time, name)())
    check("all-twelve-public-operations-declared", len(PUBLIC_OPERATIONS) == 12 and len(set(PUBLIC_OPERATIONS)) == 12)
    check("all-three-native-families-declared", len(CANDIDATES) == 3 and len(set(CANDIDATES)) == 3)
    check("baseline-is-the-unmodified-stdlib", BASELINE == "re")
    check("balanced-category-denominator", CATEGORY_COUNT * CASES_PER_CATEGORY == 33_280)
    check("original-denominator-remains-8192", ORIGINAL_CASE_COUNT == 8_192)
    check("paired-trial-denominator", PAIRED_TRIALS == 13)
    check("warmup-denominator", WARMUPS == 4)
    check("bootstrap-denominator", BOOTSTRAP_DRAWS == 2_000)
    check("raw-row-denominator", CASE_COUNT * 4 * PAIRED_TRIALS == 1_730_560)
    check("correctness-answer-denominator", CASE_COUNT * 4 * PAIRED_TRIALS * 3 == 5_191_680)
    check("confidence-interval-denominator", (CASE_COUNT + 1) * 3 == 99_843)
    check("process-and-native-denominator", CASE_COUNT * 8 + 8 == 266_248)
    check("result-limit-is-frozen", RESULT_LIMIT == 128)
    check("subject-limit-is-frozen", SUBJECT_LIMIT == 8_192)
    check("none-result-cardinality", result_cardinality(None) == 0)
    check("list-result-cardinality", result_cardinality([1, 2]) == 2)
    check("bytes-snapshot-matches-public-format", snapshot(b"ab") == {"bytes_hex": "6162"})
    check("tuples-snapshot-as-json-lists", snapshot((b"a", 2)) == [{"bytes_hex": "61"}, 2])
    check("no-candidate-imported-by-self-test", before_candidates == {name for name in sys.modules if name == "candidates" or name.startswith("candidates.")})
    check("synthetic-self-test-file-and-process-guards-exercised",
          dict(blocked_attempts)
          == {"subprocess": 1, "compressed-fixture": 1,
              "path": 1, "output": 1, "clock": len(clock_names)})
    check("synthetic-self-test-has-no-timing", "NOT MEASURED")
    subprocess.run = original_subprocess_run  # type: ignore[assignment]
    gzip.open = original_gzip_open  # type: ignore[assignment]
    Path.open = original_path_open  # type: ignore[assignment]
    os.open = original_os_open  # type: ignore[assignment]
    for clock_name, clock in original_clocks.items():
        setattr(time, clock_name, clock)
    print(json.dumps({"schema": "rebar-postfinal-public-development-self-test-v8",
                      "status": "PASS", "synthetic_controls": len(checks),
                      "controls": checks, "fixture_files_read": 0,
                      "oracle_processes_started": 0, "candidate_imports": [],
                      "case_files_written": 0, "manifest_files_written": 0,
                      "clock_samples": 0,
                      "timing": "NOT MEASURED"}, sort_keys=True))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--self-test", action="store_true", help="run synthetic, in-memory controls only")
    actions.add_argument("--freeze", action="store_true", help="explicitly prepare and exclusively freeze the public suite")
    actions.add_argument("--oracle-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--role", choices=("first", "second"), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.self_test:
        require(args.role is None, "synthetic self-test cannot become an oracle worker")
        self_test()
    elif args.oracle_worker:
        require(args.role is not None, "isolated public oracle worker role is missing")
        run_oracle_worker(args.role)
    else:
        require(args.role is None, "public freeze cannot become an oracle worker")
        freeze_public_development()


if __name__ == "__main__":
    try:
        main()
    except PublicExpansionError as error:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(error),
                          "performance": "NOT MEASURED"}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1) from error
