#!/usr/bin/env python3
"""Freeze the cumulative, first-party C20 original-native provenance fix."""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/reproduce_owned_c_original_match_semantics_source_build_v20.py"
PROTOCOL = "oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V20.md"
CONTRACT = "oracle/phase2/c-original-match-semantics-source-build-v20.json"
SCHEMA = "rebar-owned-c-original-match-semantics-source-build-v20"
VERSION = 20
DEVICE = 2064
MAX_SOURCE_BYTES = 8 * 1024 * 1024
DERIVED_SHA256 = (
    "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
)
DERIVED_BYTES = 221647
INSTALLED_SHA256 = (
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
)
INSTALLED_BYTES = 149976
INSTALLED_DEVICE = 2064
INSTALLED_INODE = 430300
INSTALLED_MODE = "0755"
PRIVATE_C18_SHA256 = (
    "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
)
PRIVATE_C18_BYTES = 163504
V19 = (
    ("tools/reproduce_owned_c_original_match_semantics_source_build_v19.py",
     "341d2f1824226b3c53faba70fe6328fc595e3a32ce77dd4a5ee007690e19dee6",
     76628, 431458),
    ("oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V19.md",
     "09deb3573a5e8595a7e485c9fc8953a357841c564b5ceca12ed624501e97f733",
     7924, 525369),
    ("oracle/phase2/c-original-match-semantics-source-build-v19.json",
     "d0d3b9780ce869d5b915609bff0d2be53880fc64efeace7eb81c4bd7682abc05",
     11147, 525370),
)
C19_FAILURE = (
    "oracle/phase2/evidence/"
    "c-original-match-semantics-source-build-v19-preactivation-failure.json",
    "5040e441e631d4063d00195193b60c3fac12e5fd56151b4f1d8d494af3acd10c",
    2139, 524804,
)
ORIGINAL_PROVENANCE = (
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V2.md",
     "bd89b3e09b1268a65475ad992b2858e2167368a82ee97d1b90b1fa36b32438b0",
     3475, 524563),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V3.md",
     "d4aa6a11d6c1398109de454f3d23e5e20d488913a00b37adfd05b47f9f53522e",
     4587, 524574),
    ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V8.md",
     "fadec2ce7e1ce8ea230dea8690db4532000c66812d76aec9ef9be290d9841d9c",
     6950, 524852),
    ("tools/run_owned_repaired_c_original_campaign_v3.py",
     "bdf846bca02c80d15e37db8d26fad45d7dacd3f3dee7ec94ce4151315423994f",
     88202, 431432),
)


class C20Error(Exception):
    """Exact cumulative first-party provenance or source authority failed."""


def need(condition: object, message: str) -> None:
    if not condition:
        raise C20Error(message)


def exact_digest(value: object, role: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require an exact independently pinned digest: " + role)
    return value


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.abspath(sys.executable) == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True,
         "require official independently pinned CPython 3.14.6 -I -B -S")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "regex" not in sys.modules and "ctypes" not in sys.modules
         and "subprocess" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject a preloaded candidate, native loader, regex engine, "
         "subprocess wrapper, or external matching package")


def read_bootstrap(owner: tuple) -> bytes:
    relative, fingerprint, count, inode = owner
    need(type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/")
         and "holdout" not in relative.lower()
         and "benchmark" not in relative.lower()
         and not relative.endswith((".so", ".gz", ".zip", ".xz", ".tar"))
         and type(count) is int and 0 < count <= MAX_SOURCE_BYTES
         and type(inode) is int and inode > 0,
         "reject live native, root, archive, graph, or unbounded bootstrap")
    exact_digest(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        first = os.fstat(descriptor)
        need(stat.S_ISREG(first.st_mode) and first.st_dev == DEVICE
             and first.st_ino == inode and first.st_size == count
             and first.st_uid == os.geteuid() and first.st_nlink == 1
             and stat.S_IMODE(first.st_mode) == 0o600,
             "reject substituted cumulative first-party owner: " + relative)
        chunks = []
        remaining = count
        while remaining:
            block = os.read(descriptor, min(remaining, 262144))
            need(bool(block), "reject truncated C20 bootstrap: " + relative)
            chunks.append(block)
            remaining -= len(block)
        need(not os.read(descriptor, 1),
             "reject trailing complete C20 bootstrap bytes: " + relative)
        payload = b"".join(chunks)
        last = os.fstat(descriptor)
        need(hashlib.sha256(payload).hexdigest() == fingerprint
             and (first.st_dev, first.st_ino, first.st_size,
                  first.st_mtime_ns, first.st_ctime_ns, first.st_nlink)
             == (last.st_dev, last.st_ino, last.st_size,
                 last.st_mtime_ns, last.st_ctime_ns, last.st_nlink),
             "reject unstable or wrongly hashed C19 bootstrap: " + relative)
        return payload
    finally:
        os.close(descriptor)


def derive_c20_controller(original: bytes) -> bytes:
    need(type(original) is bytes and len(original) == V19[0][2]
         and hashlib.sha256(original).hexdigest() == V19[0][1],
         "require the complete committed first-party C19 native-build source")
    old_hash = PRIVATE_C18_SHA256.encode("ascii")
    original_hash = INSTALLED_SHA256.encode("ascii")
    call = b"installed_path, EXPECTED_INSTALLED_NATIVE_SHA256, 163504,\n"
    corrected_call = (
        b"installed_path, EXPECTED_INSTALLED_NATIVE_SHA256, 149976, 430300,\n"
    )
    mode_anchor = b"    tools = authenticate_toolchains()\n"
    mode_check = (
        b'    need(installed_before.get("mode") == "0755"\n'
        b'         and installed_before.get("device") == 2064\n'
        b'         and installed_before.get("inode") == 430300\n'
        b'         and installed_before.get("nlink") == 1,\n'
        b'         "require exact original 0755 installed-native identity "\n'
        b'         "before any toolchain, compiler, or private build root")\n'
        + mode_anchor
    )
    need(original.count(old_hash) == 1 and original_hash not in original
         and original.count(call) == 2 and original.count(mode_anchor) == 1
         and original.count(b"VERSION = 19\n") == 1,
         "reject changed C19 baseline, ambiguous native checks, "
         "or an already-applied cumulative correction")
    need(b"075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
         not in original,
         "do not silently attribute the genuine installed original to C19")
    corrected = original.replace(old_hash, original_hash, 1)
    corrected = corrected.replace(call, corrected_call, 2)
    corrected = corrected.replace(mode_anchor, mode_check, 1)
    corrected = corrected.replace(b"v19", b"v20")
    corrected = corrected.replace(b"V19", b"V20")
    corrected = corrected.replace(b"VERSION = 19\n", b"VERSION = 20\n", 1)
    need(corrected.count(original_hash) == 1
         and old_hash not in corrected
         and corrected.count(corrected_call) == 2
         and call not in corrected
         and corrected.count(mode_check.replace(b"C19", b"C20")) == 1
         and b"VERSION = 20\n" in corrected
         and b"--authorize-first-party-native-build-v20" in corrected
         and SOURCE.encode("ascii") in corrected
         and PROTOCOL.encode("ascii") in corrected
         and CONTRACT.encode("ascii") in corrected,
         "derive only exact C20 versioning and genuine original-native "
         "hash, size, inode, mode, and pre-toolchain provenance")
    ast.parse(corrected, filename=SOURCE)
    return corrected


def document(producer: types.ModuleType, raw: bytes, role: str) -> dict:
    try:
        value = producer.JsonReader(raw).parse()
    except Exception as error:
        raise C20Error("reject malformed frozen C20 " + role + ": "
                       + str(error)) from error
    need(type(value) is dict, "require one complete source document: " + role)
    return value


def owner_record(item: tuple) -> dict:
    return {"path": item[0], "sha256": item[1], "bytes": item[2],
            "device": DEVICE, "inode": item[3], "mode": "0600", "nlink": 1}


def original_identity() -> dict:
    return {
        "sha256": INSTALLED_SHA256, "bytes": INSTALLED_BYTES,
        "device": INSTALLED_DEVICE, "inode": INSTALLED_INODE,
        "mode": INSTALLED_MODE, "nlink": 1,
    }


def validate_original_identity(value: object) -> dict:
    expected = original_identity()
    need(type(value) is dict
         and all(value.get(key) == actual for key, actual in expected.items()),
         "require exact synthetic original 075350 SHA, 149976 bytes, "
         "device 2064, inode 430300, mode 0755, and one hard link")
    return value


def validate_original_provenance(raw: dict) -> None:
    digest = INSTALLED_SHA256.encode("ascii")
    for item in ORIGINAL_PROVENANCE:
        data = raw[item[0]]
        need(digest in data,
             "require immutable independent original-native evidence: " + item[0])
    source = raw[ORIGINAL_PROVENANCE[3][0]]
    need(b'ORIGINAL_NATIVE_SHA256 = "' + digest + b'"' in source
         and b"ORIGINAL_NATIVE_BYTES = 149976" in source
         and b"ORIGINAL_NATIVE_DEVICE = 2064" in source
         and b"ORIGINAL_NATIVE_INODE = 430300" in source
         and b"ORIGINAL_NATIVE_MODE = 0o755" in source,
         "require original hash, bytes, workspace device, inode, and "
         "0755 mode from independently frozen original C source")
    for item in ORIGINAL_PROVENANCE[:3]:
        data = raw[item[0]]
        need((b"149,976" in data or b"149976" in data)
             and b"430300" in data and b"0755" in data,
             "cross-check genuine original-native identity against " + item[0])


def validate_c19_failure(value: object) -> dict:
    need(type(value) is dict
         and value.get("schema")
         == "rebar-owned-c-original-match-semantics-source-build-v19-"
            "preactivation-failure"
         and value.get("status") == "FAIL"
         and value.get("family") == "c" and value.get("version") == 19
         and value.get("phase")
         == "AUTHENTICATE INSTALLED NATIVE BEFORE TOOLCHAIN OR PRIVATE ROOT"
         and value.get("process_exit_code") == 1
         and value.get("error_type") == "BuildError"
         and value.get("error_message")
         == "reject a substituted actual owned candidate snapshot: "
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
         and value.get("source_sha256") == V19[0][1]
         and value.get("protocol_sha256") == V19[1][1]
         and value.get("contract_sha256") == V19[2][1]
         and value.get("derived_c_source_sha256") == DERIVED_SHA256
         and value.get("installed_native_relative_path")
         == "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
         and value.get("expected_installed_native_sha256")
         == PRIVATE_C18_SHA256
         and value.get("expected_installed_native_bytes") == PRIVATE_C18_BYTES
         and value.get("observed_installed_native_sha256") == INSTALLED_SHA256
         and value.get("observed_installed_native_bytes") == INSTALLED_BYTES
         and value.get("observed_installed_native_device") == INSTALLED_DEVICE
         and value.get("observed_installed_native_inode") == INSTALLED_INODE
         and value.get("observed_installed_native_mode") == INSTALLED_MODE
         and value.get("observed_installed_native_nlink") == 1
         and value.get("observed_installed_native_owner") == os.geteuid()
         and value.get("actual_compiler_process_count") == 0
         and value.get("actual_private_build_roots_created") == 0
         and value.get("actual_build_phases_completed") == 0
         and value.get("actual_build_receipts_created") == 0
         and value.get("actual_candidate_workers_started") == 0
         and value.get("native_libraries_loaded") == 0
         and value.get("original_native_file_replaced") is False
         and value.get("source_test_case_count") == 31237
         and value.get("supplemental_candidate_matching") == "NOT RUN"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("holdout") == "NOT OPENED"
         and value.get("winner_selected") is False
         and value.get("goal_sha256")
         == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
         "preserve the exact genuine, pushed, zero-compiler C19 "
         "preactivation failure and its real original-native evidence")
    need(type(value.get("observed_process_diagnostic")) is str
         and value["error_message"] in value["observed_process_diagnostic"],
         "preserve actual first-party C19 process failure diagnostics")
    return value


def bootstrap_overlay() -> types.ModuleType:
    clean_runtime()
    raw = read_bootstrap(V19[0])
    transformed = derive_c20_controller(raw)
    module = types.ModuleType("_rebar_c20_exact_first_party_c19_source_overlay")
    module.__file__ = ROOT + "/" + SOURCE
    module.__package__ = ""
    exec(compile(transformed, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SCHEMA == SCHEMA and module.VERSION == VERSION
         and module.SOURCE == SOURCE and module.PROTOCOL == PROTOCOL
         and module.CONTRACT == CONTRACT
         and module.EXPECTED_INSTALLED_NATIVE_SHA256 == INSTALLED_SHA256
         and module.DERIVED_SHA256 == DERIVED_SHA256
         and module.DERIVED_BYTES == DERIVED_BYTES
         and module.BUILD_AUTHORIZATION
         == "--authorize-first-party-native-build-v20"
         and len(module.PROCESS_ROLES) == 7 and len(module.PHASES) == 2,
         "reject incomplete or unversioned cumulative first-party C20 source")
    previous_bootstrap = module.bootstrap_wall
    previous_validate = module.validate_context
    previous_contract = module.contract_document
    previous_controls = module.source_controls
    previous_parse = module.parse_options

    def guarded_bootstrap() -> tuple:
        semantic, old, semantic_owners, base = previous_bootstrap()
        owners = base + V19 + ORIGINAL_PROVENANCE + (C19_FAILURE,)
        paths = tuple(owner[0] for owner in owners)
        module.need(len(paths) == len(frozenset(paths)),
                    "reject duplicate cumulative C20 frozen-source owners")
        old.STATIC_OWNERS = owners
        old.OWNED_PATHS = frozenset(paths) | {SOURCE, PROTOCOL, CONTRACT}
        module.need(not any(
            path == module.CANONICAL_C[0]
            or path == module.CANONICAL_ADAPTER[0]
            or path.startswith("docs/evidence/")
            or "holdout" in path.lower()
            or "benchmark" in path.lower()
            or path.endswith((".so", ".gz", ".zip", ".xz", ".tar"))
            for path in old.OWNED_PATHS
        ), "deny current candidate, native, archive, graph, root, and holdout")
        return semantic, old, semantic_owners, owners

    def guarded_validate(semantic: types.ModuleType, old: types.ModuleType,
                         semantic_owners: tuple, raw_by_path: dict,
                         producer: types.ModuleType) -> tuple:
        outcome = previous_validate(
            semantic, old, semantic_owners, raw_by_path, producer,
        )
        frozen = document(producer, raw_by_path[V19[2][0]],
                          "exact immutable previously pushed C19 source freeze")
        need(frozen.get("schema")
             == "rebar-owned-c-original-match-semantics-source-build-v19-"
                "source-freeze"
             and frozen.get("version") == 19
             and frozen.get("source", {}).get("sha256") == V19[0][1]
             and frozen.get("protocol", {}).get("sha256") == V19[1][1]
             and frozen.get("candidate_correctness") == "NOT MEASURED"
             and frozen.get("performance") == "NOT MEASURED"
             and frozen.get("holdout") == "NOT OPENED"
             and frozen.get("qualified_candidate_count") == 0,
             "authenticate committed C19 source freeze without falsely "
             "claiming its real build passed")
        historical = validate_c19_failure(document(
            producer, raw_by_path[C19_FAILURE[0]],
            "genuinely pushed small C19 preactivation failure",
        ))
        validate_original_provenance(raw_by_path)
        receipt, derived, previous_build, previous_root = outcome
        need(hashlib.sha256(derived).hexdigest() == DERIVED_SHA256
             and len(derived) == DERIVED_BYTES
             and historical["derived_c_source_sha256"] == DERIVED_SHA256,
             "retain complete exact Match-corrected source across C19 failure")
        nested = previous_root.get("root")
        need(type(nested) is dict and nested.get("device") == 2049,
             "retain receipt-only private C18 root on its real device")
        for phase in nested.get("phases", []):
            native = phase.get("native_output")
            need(type(native) is dict
                 and native.get("sha256") == PRIVATE_C18_SHA256
                 and native.get("bytes") == PRIVATE_C18_BYTES
                 and native.get("native_loaded") is False,
                 "retain f379 as a private historical C18 artifact only")
        return receipt, derived, previous_build, previous_root

    def guarded_contract(old: types.ModuleType, owners: tuple,
                         receipt: dict, previous_build: dict,
                         previous_root: dict,
                         source_sha: str, protocol_sha: str) -> dict:
        value = previous_contract(
            old, owners, receipt, previous_build, previous_root,
            source_sha, protocol_sha,
        )
        value["preserved_c19_source_freeze"] = {
            "version": 19,
            "owners": [owner_record(owner) for owner in V19],
            "source_frozen": True,
            "candidate_correctness": "NOT MEASURED",
        }
        value["actual_c19_preactivation_failure"] = {
            "receipt": owner_record(C19_FAILURE),
            "status": "FAIL",
            "phase": "AUTHENTICATE INSTALLED NATIVE BEFORE TOOLCHAIN "
                     "OR PRIVATE ROOT",
            "error_type": "BuildError",
            "incorrect_private_output_sha256": PRIVATE_C18_SHA256,
            "incorrect_private_output_bytes": PRIVATE_C18_BYTES,
            "actual_original": original_identity(),
            "actual_compiler_process_count": 0,
            "actual_private_build_roots_created": 0,
            "actual_build_phases_completed": 0,
            "actual_build_receipts_created": 0,
            "actual_candidate_workers_started": 0,
            "native_libraries_loaded": 0,
            "original_native_file_replaced": False,
            "failure_retried": False,
        }
        value["independent_original_native_provenance"] = {
            "owners": [owner_record(owner) for owner in ORIGINAL_PROVENANCE],
            "installed_original": original_identity(),
            "installed_original_read_in_source_freeze": False,
            "installed_original_replaced": False,
            "c18_private_output_is_installed_original": False,
        }
        value["cumulative_c20_correction"] = {
            "base_source": owner_record(V19[0]),
            "c19_complete_source_modified": False,
            "in_memory_c19_first_party_derivation": True,
            "corrected_installed_original_sha256": INSTALLED_SHA256,
            "corrected_installed_original_bytes": INSTALLED_BYTES,
            "corrected_installed_original_device": INSTALLED_DEVICE,
            "corrected_installed_original_inode": INSTALLED_INODE,
            "corrected_installed_original_mode": INSTALLED_MODE,
            "exact_actual_snapshot_calls_corrected": 2,
            "corrected_mode_check_precedes_toolchain": True,
            "retains_c18_private_artifact_sha256": PRIVATE_C18_SHA256,
            "retains_c18_private_artifact_bytes": PRIVATE_C18_BYTES,
            "derived_match_source_sha256": DERIVED_SHA256,
            "derived_match_source_bytes": DERIVED_BYTES,
            "candidate_correctness": "NOT MEASURED",
        }
        actual = value["future_actual_build_policy"]
        actual["installed_original_native"] = original_identity()
        actual["pushed_previous_c19_failure_sha256"] = C19_FAILURE[1]
        actual["pushed_previous_c19_contract_sha256"] = V19[2][1]
        actual["actual_original_snapshot_requires_exact_inode"] = True
        actual["actual_original_snapshot_requires_exact_mode"] = True
        actual["c18_private_output_as_installed_native"] = "FORBIDDEN"
        return value

    def guarded_controls(semantic: types.ModuleType, old: types.ModuleType,
                         wall: object, producer: types.ModuleType,
                         receipt: dict, raw_by_path: dict,
                         previous_build: dict, previous_root: dict) -> list:
        controls = previous_controls(
            semantic, old, wall, producer, receipt, raw_by_path,
            previous_build, previous_root,
        )
        failure = document(producer, raw_by_path[C19_FAILURE[0]],
                           "actual historical C19 failure hostile control")
        validate_original_identity(original_identity())

        def incorrect_original(key: str, replacement: object) -> None:
            forged = original_identity()
            forged[key] = replacement
            validate_original_identity(forged)

        def incorrect_failure(key: str, replacement: object) -> None:
            forged = dict(failure)
            forged[key] = replacement
            validate_c19_failure(forged)

        def synthetic_old_preactivation() -> None:
            observed = original_identity()
            expected = {"sha256": PRIVATE_C18_SHA256,
                        "bytes": PRIVATE_C18_BYTES}
            need(observed["sha256"] == expected["sha256"]
                 and observed["bytes"] == expected["bytes"],
                 "reproduce actual C19 synthetic original-preflight rejection "
                 "without opening installed native or creating a build root")

        checks = (
            ("replay exact synthetic failing C19 preactivation",
             synthetic_old_preactivation),
            ("reject private C18 f379 as installed original",
             lambda: incorrect_original("sha256", PRIVATE_C18_SHA256)),
            ("reject private C18 163504 bytes as installed original",
             lambda: incorrect_original("bytes", PRIVATE_C18_BYTES)),
            ("reject an altered original native device",
             lambda: incorrect_original("device", 2049)),
            ("reject an altered original native inode",
             lambda: incorrect_original("inode", INSTALLED_INODE + 1)),
            ("reject an altered original native 0755 mode",
             lambda: incorrect_original("mode", "0600")),
            ("reject an aliased original native hard link",
             lambda: incorrect_original("nlink", 2)),
            ("reject false successful historical C19 build",
             lambda: incorrect_failure("status", "PASS")),
            ("reject invented historical C19 compiler process",
             lambda: incorrect_failure("actual_compiler_process_count", 1)),
            ("reject invented historical C19 private root",
             lambda: incorrect_failure("actual_private_build_roots_created", 1)),
            ("reject false C19 phase attribution",
             lambda: incorrect_failure("phase", "BUILD NATIVE EXTENSION")),
            ("reject invented historical C19 build receipt",
             lambda: incorrect_failure("actual_build_receipts_created", 1)),
            ("reject installed native access in C20 source mode",
             lambda: os.open(
                 ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                 os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
            ("reject real private C20 root creation in source mode",
             lambda: os.mkdir(
                 "/tmp/rebar-phase2-c-original-match-semantics-v20-forbidden",
                 0o700)),
            ("reject real C20 compiler process in source mode",
             lambda: os.posix_spawn("/usr/bin/x86_64-linux-gnu-gcc-13",
                                    ["gcc", "--version"], {})),
            ("reject any stdlib matching engine in source mode",
             lambda: builtins.__import__("_sre")),
        )
        for name, action in checks:
            try:
                action()
            except Exception as error:
                need(type(error).__name__ in {
                    "BuildError", "C20Error", "CampaignError", "SourceError",
                    "ProducerError",
                }, "reject unexpected cumulative C20 hostile control: " + name)
                controls.append(name)
            else:
                raise C20Error("accepted forbidden cumulative C20 control: " + name)
        need(len(controls) >= 94 and sum(wall.blocked.values()) >= 49,
             "require complete C20 source-only hostile preactivation, "
             "native identity, archive, root, compiler, and candidate gates")
        clean_runtime()
        return controls

    def guarded_parse(arguments: list) -> dict:
        extras = {
            "--c19-source-sha256": V19[0][1],
            "--c19-protocol-sha256": V19[1][1],
            "--c19-contract-sha256": V19[2][1],
            "--c19-failure-receipt-sha256": C19_FAILURE[1],
            "--installed-original-sha256": INSTALLED_SHA256,
        }
        actual_mode = bool(arguments) and arguments[0] == "--build"
        filtered = []
        supplied = {}
        index = 0
        while index < len(arguments):
            item = arguments[index]
            if item in extras:
                need(actual_mode and item not in supplied
                     and index + 1 < len(arguments),
                     "reject duplicate, incomplete, or source-only C19 "
                     "failure and original-native build authorization")
                supplied[item] = exact_digest(arguments[index + 1], item)
                index += 2
            else:
                filtered.append(item)
                index += 1
        options = previous_parse(filtered)
        if actual_mode:
            need(supplied == extras,
                 "independently pin the complete previous C19 freeze, "
                 "actual failure, and true installed original before C20 build")
            options.update(supplied)
        else:
            need(not supplied,
                 "reject actual native provenance authority in source-only mode")
        return options

    module.bootstrap_wall = guarded_bootstrap
    module.validate_context = guarded_validate
    module.contract_document = guarded_contract
    module.source_controls = guarded_controls
    module.parse_options = guarded_parse
    clean_runtime()
    return module


def main() -> int:
    try:
        clean_runtime()
        controller = bootstrap_overlay()
        return controller.main()
    except Exception as error:
        sys.stderr.write("C original Match source build V20: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
