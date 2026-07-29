#!/usr/bin/env python3
"""Prove an exact, in-memory, first-party Rust scanner metadata repair."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "inspect")):
    raise SystemExit("scanner source verification started with a regex dependency")

import builtins
import hashlib
import os
import stat

ROOT = "/home/dev-user/src/rebar"
PINNED_CPYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_CPYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
SOURCE_PATH = "tools/verify_owned_rust_scanner_signature_source_v22.py"
PROTOCOL_PATH = "oracle/phase2/RUST-SCANNER-SIGNATURE-SOURCE-REPAIR-V22.md"
CONTRACT_PATH = "oracle/phase2/rust-scanner-signature-source-repair-v22.json"
PREDECESSOR_PATH = (
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/"
    "py_bridge.c"
)
PREDECESSOR_SHA256 = (
    "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
)
PREDECESSOR_BYTES = 179520
VARIANT_PATH = (
    "candidates/rust/variants/"
    "buffer_shape_pickle_findall_captures_scanner_signature_v22/py_bridge.c"
)
VARIANT_SHA256 = (
    "6639104f618b5a905d0883b02e5183b9a3b6ac6db0587b1dfa7b074990f3bb75"
)
VARIANT_BYTES = 179482
V21_BUILD_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v21-rust-phase2-v21-rust-captured-findall-"
    "root-provenance-publication-receipt.json"
)
V21_BUILD_RECEIPT_SHA256 = (
    "bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102"
)
V21_ROOT_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v21-rust-phase2-v21-rust-captured-findall-"
    "root-provenance-root-provenance-receipt.json"
)
V21_ROOT_RECEIPT_SHA256 = (
    "73cee9c0a4f44d113da96b505eb0e9224577584b75c347e6fd351995d1d09a4e"
)
CALLABLE_RECEIPT_PATH = (
    "oracle/phase1/evidence/"
    "callable-introspection-reference-v2-cpython-3.14.6-"
    "publication-receipt.json"
)
CALLABLE_RECEIPT_SHA256 = (
    "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334"
)
SCHEMA = "rebar-phase2-owned-rust-scanner-signature-source-repair-v22"
MAX_OWNER_BYTES = 512 * 1024

OLD_SEARCH = (
    b'    {"search", (PyCFunction)rust_scanner_search, METH_NOARGS, '
    b'"Search for the next regular-expression match."},\n'
)
NEW_SEARCH = (
    b'    {"search", (PyCFunction)rust_scanner_search, METH_NOARGS, '
    b'"search($self, /)\\n--\\n\\n"},\n'
)
OLD_MATCH = (
    b'    {"match", (PyCFunction)rust_scanner_match, METH_NOARGS, '
    b'"Match at the scanner\'s current position."},\n'
)
NEW_MATCH = (
    b'    {"match", (PyCFunction)rust_scanner_match, METH_NOARGS, '
    b'"match($self, /)\\n--\\n\\n"},\n'
)
ARRAY_START = b"static PyMethodDef rust_scanner_methods[] = {\n"
ARRAY_END = b"\n};\n\nstatic PyGetSetDef rust_iterator_getsets[] = {\n"
FASTCALL_BLOCK = (
    b"static PyMethodDef rust_iterator_scanner_search_method = {\n"
    b'    "search",\n'
    b"    _PyCFunction_CAST(rust_iterator_scanner_search),\n"
    b"    METH_METHOD | METH_FASTCALL | METH_KEYWORDS,\n"
    b'    "Search for the next regular-expression match.",\n'
    b"};\n"
)
CASE_IDS = (
    "callable-introspection.v1.scanner.03.unbound.compiled-scanner.match",
    "callable-introspection.v1.scanner.04.bound.compiled-scanner.match",
    "callable-introspection.v1.scanner.05.unbound.compiled-scanner.search",
    "callable-introspection.v1.scanner.06.bound.compiled-scanner.search",
)

FIXED_OWNERS = (
    (
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3756,
    ),
    (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261,
    ),
    (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875,
    ),
    (
        "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
        "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        3929,
    ),
    (
        "oracle/phase1/p0-differential-fuzz-reference-v3.json",
        "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
        5288,
    ),
    (
        "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
        8952,
    ),
    (
        "oracle/phase1/p0-callable-introspection-v1.json",
        "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
        14749,
    ),
    (
        "oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md",
        "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f",
        7487,
    ),
    (
        "oracle/phase1/callable-introspection-reference-v2.json",
        "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42",
        7253,
    ),
    (CALLABLE_RECEIPT_PATH, CALLABLE_RECEIPT_SHA256, 3533),
    (
        "tools/reproduce_owned_rust_captured_findall_source_build_v21.py",
        "bc5f5b4efd8b20a564692e14f972c77267c58ac44a560b432a0a1cc38e794c58",
        100150,
    ),
    (
        "oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md",
        "d7c137d2432c2f28f4b6b26fdde3a591b92f7d62e6018d047cfa0b3ccfe0a8c4",
        4943,
    ),
    (
        "oracle/phase2/rust-captured-findall-source-build-v21.json",
        "61e14e1d47f55759a73721635594b69ba098541bc83c9046c99c0c282223fd4a",
        18420,
    ),
    (V21_BUILD_RECEIPT_PATH, V21_BUILD_RECEIPT_SHA256, 3502),
    (V21_ROOT_RECEIPT_PATH, V21_ROOT_RECEIPT_SHA256, 6306),
    (PREDECESSOR_PATH, PREDECESSOR_SHA256, PREDECESSOR_BYTES),
    (
        "tools/verify_expanded_sealed_holdout_v1.py",
        "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
        27311,
    ),
    (
        "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
        "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
        13237,
    ),
    (
        "oracle/phase3/expanded-sealed-holdout-v1.json",
        "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
        6628,
    ),
)
ALLOWED_OWNER_PATHS = frozenset(
    os.path.join(ROOT, relative)
    for relative in (
        SOURCE_PATH,
        PROTOCOL_PATH,
        CONTRACT_PATH,
        *(entry[0] for entry in FIXED_OWNERS),
    )
)
FORBIDDEN_IMPORTS = frozenset(
    (
        "re",
        "_sre",
        "regex",
        "inspect",
        "ctypes",
        "subprocess",
        "multiprocessing",
        "socket",
        "time",
        "gzip",
        "bz2",
        "lzma",
        "tarfile",
        "zipfile",
    )
)
FORBIDDEN_AUDIT_EVENTS = frozenset(
    (
        "subprocess.Popen",
        "os.system",
        "os.posix_spawn",
        "os.posix_spawnp",
        "os.spawn",
        "os.fork",
        "os.forkpty",
        "os.remove",
        "os.rmdir",
        "os.mkdir",
        "os.rename",
        "os.chmod",
        "os.chown",
        "os.truncate",
        "os.link",
        "os.symlink",
        "os.listdir",
        "os.scandir",
        "os.putenv",
        "os.unsetenv",
        "ctypes.dlopen",
        "ctypes.dlsym",
        "socket.__new__",
        "socket.connect",
        "socket.bind",
        "socket.sendto",
        "time.sleep",
    )
)


class FreezeError(Exception):
    """A first-party, two-site, source-only proof could not be established."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def valid_sha256(value: object, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        label + " must contain exactly 64 lowercase hexadecimal characters",
    )
    return value


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "authenticated source must contain exact bytes")
    return hashlib.sha256(raw).hexdigest()


def quote(value: str) -> str:
    require(type(value) is str, "canonical evidence requires exact strings")
    escapes = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\f": "\\f",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
    pieces = ['"']
    for character in value:
        point = ord(character)
        require(
            not 0xD800 <= point <= 0xDFFF,
            "canonical evidence cannot contain unpaired surrogates",
        )
        if character in escapes:
            pieces.append(escapes[character])
        elif point < 32:
            pieces.append("\\u" + format(point, "04x"))
        else:
            pieces.append(character)
    pieces.append('"')
    return "".join(pieces)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= 32, "canonical evidence exceeds its maximum nesting depth")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return quote(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(
            all(type(key) is str for key in value),
            "canonical evidence requires exact string keys",
        )
        return "{" + ",".join(
            quote(key) + ":" + canonical(value[key], depth + 1)
            for key in sorted(value)
        ) + "}"
    raise FreezeError("canonical evidence contains an unsupported value")


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_AUDIT_EVENTS:
        raise FreezeError("source-only verification denied " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if type(name) is str and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise FreezeError("source-only verification denied import " + name)
        return
    if event != "open":
        return
    require(len(arguments) >= 3, "source-only verification denied an unknown open")
    path, mode, flags = arguments[:3]
    require(type(path) is str, "source-only verification denied descriptor access")
    require(
        path in ALLOWED_OWNER_PATHS,
        "source-only verification denied an unlisted file or sealed case",
    )
    require(
        mode in ("r", "rb"),
        "source-only verification denied a writable open mode",
    )
    require(
        type(flags) is int
        and (flags & os.O_ACCMODE) == os.O_RDONLY
        and not (flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND)),
        "source-only verification denied writable open flags",
    )


def read_owner(path: str, expected_hash: str, expected_size: int) -> bytes:
    valid_sha256(expected_hash, path + " SHA-256")
    require(type(path) is str and path and not os.path.isabs(path), "invalid owner path")
    require(
        type(expected_size) is int and 0 < expected_size <= MAX_OWNER_BYTES,
        "source owner exceeds the bounded read limit",
    )
    absolute = os.path.join(ROOT, path)
    require(absolute in ALLOWED_OWNER_PATHS, "source owner is not explicitly allowed")
    info = os.lstat(absolute)
    require(stat.S_ISREG(info.st_mode), "source owner must be a regular, non-link file")
    require(info.st_size == expected_size, "source-owner byte count changed")
    with builtins.open(absolute, "rb") as source:
        raw = source.read(MAX_OWNER_BYTES + 1)
        require(source.read(1) == b"", "source owner changed during bounded reading")
    require(len(raw) == expected_size, "source-owner read length changed")
    require(digest(raw) == expected_hash, "source-owner SHA-256 changed")
    return raw


def pinned_interpreter() -> None:
    require(sys.executable == PINNED_CPYTHON, "the frozen CPython executable is required")
    require(
        sys.implementation.name == "cpython" and sys.version_info[:3] == (3, 14, 6),
        "the frozen CPython 3.14.6 reference is required",
    )
    require(sys.flags.isolated == 1, "source verification requires isolated -I")
    require(sys.dont_write_bytecode, "source verification requires no-bytecode -B")
    require(sys.flags.no_site == 1, "source verification requires no-site -S")
    require(
        not any(name in sys.modules for name in ("re", "_sre", "regex", "inspect")),
        "source verification cannot load a regular-expression or signature engine",
    )


def derive_variant(predecessor: bytes) -> bytes:
    require(type(predecessor) is bytes, "the cumulative predecessor must be exact bytes")
    require(len(predecessor) == PREDECESSOR_BYTES, "the captured bridge size changed")
    require(
        digest(predecessor) == PREDECESSOR_SHA256,
        "the independently built captured bridge SHA-256 changed",
    )
    require(predecessor.count(ARRAY_START) == 1, "scanner method table is not unique")
    require(predecessor.count(ARRAY_END) == 1, "scanner method table end is not unique")
    start = predecessor.index(ARRAY_START) + len(ARRAY_START)
    finish = predecessor.index(ARRAY_END, start)
    table = predecessor[start:finish]
    require(table.count(OLD_SEARCH) == 1, "scanner search metadata is not unique")
    require(table.count(OLD_MATCH) == 1, "scanner match metadata is not unique")
    require(predecessor.count(OLD_SEARCH) == 1, "search metadata occurs outside its table")
    require(predecessor.count(OLD_MATCH) == 1, "match metadata occurs outside its table")
    require(NEW_SEARCH not in predecessor, "search correction is unexpectedly present")
    require(NEW_MATCH not in predecessor, "match correction is unexpectedly present")
    require(predecessor.count(FASTCALL_BLOCK) == 1, "distinct fastcall metadata changed")
    require(
        predecessor.count(b'.name = "_sre.SRE_Scanner",') == 1,
        "the Python-compatible scanner display type changed",
    )
    require(
        predecessor.count(b"static PyObject *rust_bound_get_signature(") == 1,
        "unrelated existing bound-method signature implementation changed",
    )
    variant = predecessor.replace(OLD_SEARCH, NEW_SEARCH, 1)
    variant = variant.replace(OLD_MATCH, NEW_MATCH, 1)
    require(len(variant) == VARIANT_BYTES, "derived scanner variant has the wrong size")
    require(digest(variant) == VARIANT_SHA256, "derived scanner variant has the wrong hash")
    require(variant.count(NEW_SEARCH) == 1, "corrected search metadata is not unique")
    require(variant.count(NEW_MATCH) == 1, "corrected match metadata is not unique")
    require(OLD_SEARCH not in variant, "obsolete scanner search metadata remains")
    require(OLD_MATCH not in variant, "obsolete scanner match metadata remains")
    require(variant.count(FASTCALL_BLOCK) == 1, "unrelated fastcall metadata changed")
    restored = variant.replace(NEW_SEARCH, OLD_SEARCH, 1)
    restored = restored.replace(NEW_MATCH, OLD_MATCH, 1)
    require(restored == predecessor, "bytes outside the exact two metadata edits changed")
    return variant


def contract_model(
    source_hash: str,
    source_size: int,
    protocol_hash: str,
    protocol_size: int,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 22,
        "status": "SOURCE FROZEN; VARIANT NOT BUILT; NOT RUN; NOT BENCHMARKED",
        "family": "rust",
        "source": {
            "path": SOURCE_PATH,
            "sha256": source_hash,
            "bytes": source_size,
            "writes_permitted": False,
        },
        "protocol": {
            "path": PROTOCOL_PATH,
            "sha256": protocol_hash,
            "bytes": protocol_size,
        },
        "frozen_python_reference": {
            "cpython": "3.14.6",
            "executable": PINNED_CPYTHON,
            "historically_authenticated_executable_sha256": PINNED_CPYTHON_SHA256,
            "original_cases": 31237,
            "original_groups": 13,
            "named_private_waivers": 13,
            "additional_differential_property_cases": 8244,
            "additional_callable_introspection_cases": 50,
            "additional_cases_in_original_denominator": False,
            "callable_reference_receipt": {
                "path": CALLABLE_RECEIPT_PATH,
                "sha256": CALLABLE_RECEIPT_SHA256,
                "bytes": 3533,
                "reference_status": "PASS",
                "candidate_observation": "NOT MEASURED",
            },
        },
        "independently_built_immediate_predecessor": {
            "path": PREDECESSOR_PATH,
            "sha256": PREDECESSOR_SHA256,
            "bytes": PREDECESSOR_BYTES,
            "first_party_engine": True,
            "external_regex_dependencies": 0,
            "inherits_literal_and_captured_findall_features": True,
            "actual_compiler_process_count": 28,
            "actual_source_phase_count": 2,
            "native_build_status": "PASS",
            "candidate_correctness": "NOT MEASURED",
            "publication_receipt": {
                "path": V21_BUILD_RECEIPT_PATH,
                "sha256": V21_BUILD_RECEIPT_SHA256,
                "bytes": 3502,
            },
            "root_provenance_receipt": {
                "path": V21_ROOT_RECEIPT_PATH,
                "sha256": V21_ROOT_RECEIPT_SHA256,
                "bytes": 6306,
            },
        },
        "candidate_variant": {
            "path": VARIANT_PATH,
            "source_representation": "DETERMINISTIC IN-MEMORY OVERLAY; NOT MATERIALIZED",
            "sha256": VARIANT_SHA256,
            "bytes": VARIANT_BYTES,
            "changed_method_metadata_count": 2,
            "changed_matching_functions": 0,
            "all_other_predecessor_bytes_unchanged": True,
            "first_party_matching_engine_unchanged": True,
            "distinct_fastcall_scanner_unchanged": True,
            "native_scanner_display_name": "_sre.SRE_Scanner",
            "display_name_is_an_import": False,
            "existing_bound_signature_implementation_unchanged": True,
            "native_build": "NOT RUN",
            "matching": "NOT RUN",
            "qualified": False,
        },
        "predicted_frozen_scanner_obligations": {
            "case_ids": list(CASE_IDS),
            "case_count": 4,
            "prediction_basis": "AUTHENTICATED SOURCE AND PASSING PYTHON REFERENCE",
            "candidate_observation": "NOT MEASURED",
            "unbound_signature": "(self, /)",
            "bound_signature": "()",
            "text_signature": "($self, /)",
            "documentation": None,
        },
        "expanded_sealed_holdout_proposal": {
            "case_count": 14155776,
            "historical_previous_proposal_case_count": 4194304,
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
            "generator_status": "NOT FROZEN",
            "case_status": "NOT GENERATED; NOT OPENED",
            "minimum_qualified_independent_family_count": 3,
            "qualified_independent_family_count": 0,
            "runtime_independence_status": "NOT ESTABLISHED",
        },
        "required_future_gates": {
            "fresh_variant_native_build_and_provenance": "NOT RUN",
            "complete_original_correctness": "NOT RUN",
            "complete_additional_correctness": "NOT RUN",
            "public_api_and_buffer_correctness": "NOT RUN",
            "callable_introspection_candidate": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "phase_boundary": {
            "archive_opens": 0,
            "private_build_roots_opened": 0,
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "matching_operations": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "files_written": 0,
            "holdout": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "holdout_case_count": 14155776,
            "qualified_candidate_count": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def parse_arguments(arguments: list[str]) -> tuple[str, str, str, str | None]:
    require(type(arguments) is list, "arguments must be an exact argument list")
    require(arguments, "select one source-only verification mode")
    mode = arguments[0]
    require(
        mode in ("--self-test", "--verify-frozen-context", "--render-contract"),
        "select exactly one supported source-only verification mode",
    )
    options = arguments[1:]
    require(len(options) % 2 == 0, "every frozen owner must have its SHA-256")
    values: dict[str, str] = {}
    for index in range(0, len(options), 2):
        name = options[index]
        require(
            name in ("--source-sha256", "--protocol-sha256", "--contract-sha256"),
            "source-only verification rejects unknown or writable options",
        )
        require(name not in values, "source-only verification rejects duplicate options")
        values[name] = valid_sha256(options[index + 1], name)
    required = {"--source-sha256", "--protocol-sha256"}
    if mode != "--render-contract":
        required.add("--contract-sha256")
    require(set(values) == required, "supply exactly the required frozen-owner hashes")
    return (
        mode,
        values["--source-sha256"],
        values["--protocol-sha256"],
        values.get("--contract-sha256"),
    )


def verify_context(
    source_hash: str,
    protocol_hash: str,
    contract_hash: str | None,
) -> tuple[dict[str, object], bytes]:
    pinned_interpreter()
    source_info = os.lstat(os.path.join(ROOT, SOURCE_PATH))
    protocol_info = os.lstat(os.path.join(ROOT, PROTOCOL_PATH))
    source = read_owner(SOURCE_PATH, source_hash, source_info.st_size)
    protocol = read_owner(PROTOCOL_PATH, protocol_hash, protocol_info.st_size)
    owners: dict[str, bytes] = {}
    for path, expected_hash, expected_size in FIXED_OWNERS:
        require(path not in owners, "source-only ownership contains a duplicate path")
        owners[path] = read_owner(path, expected_hash, expected_size)
    predecessor = owners[PREDECESSOR_PATH]
    variant = derive_variant(predecessor)
    callable_matrix = owners["oracle/phase1/p0-callable-introspection-v1.json"]
    for case_id in CASE_IDS:
        require(
            callable_matrix.count(quote(case_id).encode("ascii")) == 1,
            "the predicted scanner case is not uniquely frozen",
        )
    callable_receipt = owners[CALLABLE_RECEIPT_PATH]
    require(
        b'"reference_status":"PASS"' in callable_receipt,
        "the independent Python callable reference is not passing",
    )
    require(
        b'"candidate_introspection":"NOT MEASURED"' in callable_receipt,
        "a Python reference cannot stand in for a candidate observation",
    )
    build_receipt = owners[V21_BUILD_RECEIPT_PATH]
    root_receipt = owners[V21_ROOT_RECEIPT_PATH]
    for receipt in (build_receipt, root_receipt):
        require(b'"status":"PASS"' in receipt, "actual V21 native receipt is not passing")
        require(
            PREDECESSOR_SHA256.encode("ascii") in receipt,
            "actual V21 native receipt is not bound to the immediate predecessor",
        )
        require(
            b'"candidate_correctness":"NOT MEASURED"' in receipt,
            "native compilation cannot establish candidate correctness",
        )
    require(
        b'"actual_compiler_process_count":28' in build_receipt,
        "actual captured Rust build must preserve its 28 real processes",
    )
    require(
        b'"actual_source_phase_count":2' in root_receipt,
        "actual captured Rust build must preserve two independent phases",
    )
    model = contract_model(source_hash, len(source), protocol_hash, len(protocol))
    raw_contract = (canonical(model) + "\n").encode("utf-8")
    if contract_hash is not None:
        actual_contract = read_owner(CONTRACT_PATH, contract_hash, len(raw_contract))
        require(actual_contract == raw_contract, "frozen contract is not exactly canonical")
    pinned_interpreter()
    require(len(variant) == VARIANT_BYTES, "verified variant size unexpectedly changed")
    return model, raw_contract


def expect_failure(callback: object, message: str) -> None:
    require(callable(callback), "hostile control requires a callable")
    try:
        callback()
    except FreezeError:
        return
    raise FreezeError("hostile control unexpectedly succeeded: " + message)


def self_test(predecessor: bytes) -> tuple[int, int]:
    positive = 0
    hostile = 0
    variant = derive_variant(predecessor)
    for _ in range(8):
        require(derive_variant(predecessor) == variant, "source transform is nondeterministic")
        positive += 1
    require(digest(variant) == VARIANT_SHA256, "derived source hash is not reproducible")
    positive += 1
    require(variant.count(FASTCALL_BLOCK) == 1, "distinct fastcall method was changed")
    positive += 1
    for case_id in CASE_IDS:
        require(case_id.startswith("callable-introspection.v1.scanner."), "wrong case owner")
        positive += 1
    for index in range(128):
        position = (index * 7919 + 17) % len(predecessor)
        altered = (
            predecessor[:position]
            + bytes((predecessor[position] ^ (1 << (index % 8)),))
            + predecessor[position + 1 :]
        )
        expect_failure(lambda value=altered: derive_variant(value), "modified bridge byte")
        hostile += 1
    broken_sources = (
        b"",
        predecessor[:-1],
        predecessor + b"\n",
        predecessor.replace(OLD_SEARCH, OLD_SEARCH + OLD_SEARCH, 1),
        predecessor.replace(OLD_MATCH, OLD_MATCH + OLD_MATCH, 1),
        predecessor.replace(OLD_SEARCH, NEW_SEARCH, 1),
        predecessor.replace(OLD_MATCH, NEW_MATCH, 1),
        predecessor.replace(FASTCALL_BLOCK, b"", 1),
        variant,
    )
    for broken in broken_sources:
        expect_failure(lambda value=broken: derive_variant(value), "unauthenticated source")
        hostile += 1
    for invalid in ("", "a" * 63, "a" * 65, "A" * 64, "g" * 64, 0, None):
        expect_failure(lambda value=invalid: valid_sha256(value, "control"), "bad hash")
        hostile += 1
    for event in FORBIDDEN_AUDIT_EVENTS:
        expect_failure(lambda name=event: audit_wall(name, ()), "forbidden audit event")
        hostile += 1
    for name in FORBIDDEN_IMPORTS:
        expect_failure(lambda value=name: audit_wall("import", (value,)), "forbidden import")
        hostile += 1
        expect_failure(
            lambda value=name: audit_wall("import", (value + ".nested",)),
            "forbidden nested import",
        )
        hostile += 1
    allowed = os.path.join(ROOT, SOURCE_PATH)
    bad_opens = (
        (os.path.join(ROOT, ".sealed-holdout"), "rb", os.O_RDONLY),
        (os.path.join(ROOT, "oracle/phase2/evidence/forbidden.json.gz"), "rb", os.O_RDONLY),
        ("/tmp/rebar-phase2-native-build-v9-rust-private", "rb", os.O_RDONLY),
        (allowed, "wb", os.O_WRONLY | os.O_CREAT | os.O_TRUNC),
        (allowed, "ab", os.O_WRONLY | os.O_CREAT | os.O_APPEND),
        (allowed, "r+", os.O_RDWR),
        (allowed, "rb", os.O_RDWR),
        (allowed, "rb", os.O_RDONLY | os.O_TRUNC),
        (3, "rb", os.O_RDONLY),
    )
    for arguments in bad_opens:
        expect_failure(lambda value=arguments: audit_wall("open", value), "unsafe owner open")
        hostile += 1
    audit_wall("open", (allowed, "rb", os.O_RDONLY))
    positive += 1
    for invalid in (0.5, b"bytes", {1: "bad"}, object()):
        expect_failure(lambda value=invalid: canonical(value), "unsupported canonical value")
        hostile += 1
    for invalid in ("\ud800", "\udfff"):
        expect_failure(lambda value=invalid: quote(value), "unpaired Unicode surrogate")
        hostile += 1
    known = "a" * 64
    malformed_arguments = (
        [],
        ["--run"],
        ["--build"],
        ["--write-variant"],
        ["--self-test"],
        ["--self-test", "--source-sha256", known],
        ["--render-contract", "--source-sha256", known],
        ["--render-contract", "--source-sha256", known, "--protocol-sha256", known,
         "--contract-sha256", known],
        ["--self-test", "--source-sha256", known, "--source-sha256", known,
         "--protocol-sha256", known, "--contract-sha256", known],
    )
    for arguments in malformed_arguments:
        expect_failure(lambda value=arguments: parse_arguments(value), "unsafe command mode")
        hostile += 1
    require(positive >= 15, "insufficient positive source-only controls")
    require(hostile >= 200, "insufficient hostile source-only controls")
    return positive, hostile


def main() -> int:
    mode, source_hash, protocol_hash, contract_hash = parse_arguments(sys.argv[1:])
    sys.addaudithook(audit_wall)
    model, raw_contract = verify_context(source_hash, protocol_hash, contract_hash)
    if mode == "--render-contract":
        sys.stdout.write(raw_contract.decode("utf-8"))
        return 0
    result: dict[str, object] = {
        "status": "PASS",
        "mode": mode,
        "schema": SCHEMA,
        "source_sha256": source_hash,
        "protocol_sha256": protocol_hash,
        "contract_sha256": contract_hash,
        "predecessor_sha256": PREDECESSOR_SHA256,
        "variant_sha256": VARIANT_SHA256,
        "variant_bytes": VARIANT_BYTES,
        "changed_method_metadata_count": 2,
        "candidate_observation": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "holdout_case_count": 14155776,
        "hidden_cases_read": 0,
        "archive_opens": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
    }
    if mode == "--self-test":
        predecessor = read_owner(PREDECESSOR_PATH, PREDECESSOR_SHA256, PREDECESSOR_BYTES)
        positive, hostile = self_test(predecessor)
        result["positive_controls_passed"] = positive
        result["hostile_controls_rejected"] = hostile
    else:
        result["authenticated_frozen_owners"] = len(FIXED_OWNERS) + 3
        result["predicted_case_ids"] = list(CASE_IDS)
        result["prediction_is_candidate_observation"] = False
        result["v21_actual_compiler_process_count"] = 28
        result["v21_actual_source_phase_count"] = 2
    require(model["family"] == "rust", "first-party Rust source model changed")
    pinned_interpreter()
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, ValueError, UnicodeError) as failure:
        sys.stderr.write("SOURCE-ONLY VERIFICATION FAILED: " + str(failure) + "\n")
        raise SystemExit(1)
