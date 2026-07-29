#!/usr/bin/env python3
"""Freeze the portable, cumulative first-party C Match native build V21."""

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
SOURCE = "tools/reproduce_owned_c_original_match_semantics_source_build_v21.py"
PROTOCOL = "oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V21.md"
CONTRACT = "oracle/phase2/c-original-match-semantics-source-build-v21.json"
SCHEMA = "rebar-owned-c-original-match-semantics-source-build-v21"
VERSION = 21
DEVICE = 2064
MAX_OWNER_BYTES = 8 * 1024 * 1024
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
C20 = (
    ("tools/reproduce_owned_c_original_match_semantics_source_build_v20.py",
     "0aea50642a1f1322f6e5b84e1ea09f2899e3fe779d61eecafb1b4c8e9d5fdf62",
     28211, 429057),
    ("oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V20.md",
     "a2e4ef1c906b389073ae7d27aebf4e934fce5e8858416f4ccad4461243440421",
     7453, 524805),
    ("oracle/phase2/c-original-match-semantics-source-build-v20.json",
     "f5264d141748e01651f2203e6e23060fe3b9f0f472f8b2d86c55e91a97d821da",
     15641, 524806),
)
C20_FAILURE = (
    "oracle/phase2/evidence/"
    "c-original-match-semantics-source-build-v20-preactivation-failure.json",
    "88bc4bf0b1037a00bc426f0121dac601a9433e0d0090aae483d03a620b995d47",
    5111, 524814,
)
C19 = (
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


class C21Error(Exception):
    """The complete cumulative first-party portable build failed closed."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise C21Error(reason)


def exact_digest(value: object, role: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require an independently pinned complete digest: " + role)
    return value


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.abspath(sys.executable) == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True,
         "require matcher-free official CPython 3.14.6 -I -B -S")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "regex" not in sys.modules and "ctypes" not in sys.modules
         and "subprocess" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject matcher, fallback, candidate, native loader, or subprocess")


def read_bootstrap(owner: tuple) -> bytes:
    relative, fingerprint, size, inode = owner
    need(type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/")
         and "holdout" not in relative.lower()
         and "benchmark" not in relative.lower()
         and not relative.endswith((".so", ".gz", ".tar", ".zip", ".xz"))
         and type(size) is int and 0 < size <= MAX_OWNER_BYTES
         and type(inode) is int and inode > 0,
         "reject actual native, root, compressed report, or oversized owner")
    exact_digest(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == size
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted immutable C20 first-party owner: " + relative)
        parts = []
        remaining = size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            need(bool(chunk), "reject a truncated C21 bootstrap: " + relative)
            parts.append(chunk)
            remaining -= len(chunk)
        need(not os.read(descriptor, 1),
             "reject extra complete C20 source bytes: " + relative)
        raw = b"".join(parts)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject changed or incorrectly authenticated cumulative C20 source")
        return raw
    finally:
        os.close(descriptor)


def document(producer: types.ModuleType, raw: bytes, role: str) -> dict:
    try:
        value = producer.JsonReader(raw).parse()
    except Exception as error:
        raise C21Error("reject malformed exact C21 " + role + ": "
                       + str(error)) from error
    need(type(value) is dict, "require one complete machine document: " + role)
    return value


def owner_record(item: tuple) -> dict:
    return {"path": item[0], "sha256": item[1], "bytes": item[2],
            "device": DEVICE, "inode": item[3], "mode": "0600", "nlink": 1}


def installed_identity() -> dict:
    return {"sha256": INSTALLED_SHA256, "bytes": INSTALLED_BYTES,
            "device": INSTALLED_DEVICE, "inode": INSTALLED_INODE,
            "mode": INSTALLED_MODE, "nlink": 1}


def validate_c20_failure(value: object, module: types.ModuleType) -> dict:
    need(type(value) is dict
         and value.get("schema")
         == "rebar-owned-c-original-match-semantics-source-build-v20-"
            "actual-preactivation-failure"
         and value.get("version") == 20
         and value.get("status") == "FAIL"
         and value.get("failure_retried") is False
         and value.get("exit_code") == 1
         and value.get("failure_phase")
         == "GENERATE PRIVATE ROOT RANDOMNESS AFTER TOOLCHAIN "
            "AUTHENTICATION AND BEFORE DIRECTORY CREATION"
         and value.get("error_type") == "AttributeError"
         and value.get("error_message")
         == "module 'os' has no attribute 'getrandom'"
         and value.get("source_sha256") == C20[0][1]
         and value.get("protocol_sha256") == C20[1][1]
         and value.get("contract_sha256") == C20[2][1]
         and value.get("explicit_build_authorization")
         == "--authorize-first-party-native-build-v20"
         and value.get("independently_pinned_build_authority_count") == 26
         and value.get("pinned_cpython_version") == "3.14.6"
         and value.get("os_getrandom_available") is False
         and value.get("os_urandom_available") is True
         and value.get("failed_private_root_randomness_api")
         == "os.getrandom(16)"
         and value.get("unreached_journal_randomness_api")
         == "os.getrandom(12)"
         and value.get("authenticated_toolchain_owner_count") == 5
         and value.get("actual_private_build_roots_created") == 0
         and value.get("actual_private_build_roots_opened") == 0
         and value.get("actual_build_phases_completed") == 0
         and value.get("actual_phase_source_owners_created") == 0
         and value.get("actual_compiler_process_count") == 0
         and value.get("actual_recovery_journals_created") == 0
         and value.get("actual_build_receipts_created") == 0
         and value.get("actual_root_receipts_created") == 0
         and value.get("actual_candidate_workers_started") == 0
         and value.get("actual_native_libraries_loaded") == 0
         and value.get("installed_original_before") == installed_identity()
         and value.get("installed_original_after") == installed_identity()
         and value.get("installed_native_activated") is False
         and value.get("original_native_file_replaced") is False
         and value.get("historical_archives_opened") == 0
         and value.get("hidden_cases_read") == 0
         and value.get("original_case_execution_denominator") == 31237
         and value.get("separate_additional_reference_case_count") == 8244
         and value.get("expanded_holdout_proposed_case_count") == 14155776
         and value.get("expanded_holdout_status")
         == "NOT FROZEN; NOT GENERATED; NOT OPENED"
         and value.get("candidate_correctness") == "NOT MEASURED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("undefined_behavior") == "NOT MEASURED"
         and value.get("qualified_candidate_count") == 0
         and value.get("winner_selected") is False
         and value.get("goal_sha256")
         == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
         "preserve the exact genuinely pushed C20 five-toolchain, zero-root "
         "portable-randomness failure and unchanged true installed original")
    authority = value.get("independently_pinned_build_authority")
    expected = {
        "source_sha256": C20[0][1],
        "protocol_sha256": C20[1][1],
        "contract_sha256": C20[2][1],
        "semantic_source_sha256": module.SEMANTICS[0][1],
        "semantic_protocol_sha256": module.SEMANTICS[1][1],
        "semantic_contract_sha256": module.SEMANTICS[2][1],
        "phase1_source_sha256": module.P0_PIN[0]
        if hasattr(module, "P0_PIN") else
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        "phase1_protocol_sha256":
            "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        "phase1_contract_sha256":
            "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        "guard_source_sha256":
            "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        "guard_protocol_sha256":
            "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        "guard_contract_sha256":
            "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        "producer_source_sha256":
            "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        "producer_protocol_sha256":
            "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        "producer_contract_sha256":
            "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        "c18_source_sha256": module.C18[0][1],
        "c18_protocol_sha256": module.C18[1][1],
        "c18_contract_sha256": module.C18[2][1],
        "c18_build_receipt_sha256": module.C18_BUILD_RECEIPT[1],
        "c18_root_receipt_sha256": module.C18_ROOT_RECEIPT[1],
        "derived_variant_sha256": DERIVED_SHA256,
        "c19_source_sha256": C19[0][1],
        "c19_protocol_sha256": C19[1][1],
        "c19_contract_sha256": C19[2][1],
        "c19_failure_receipt_sha256": C19_FAILURE[1],
        "installed_original_sha256": INSTALLED_SHA256,
    }
    need(type(authority) is dict and authority == expected
         and len(authority) == 26,
         "require every one of the 26 genuinely used C20 native "
         "authorities, including C19 failure and installed-original identity")
    return value


def derive_c21_wrapper(raw: bytes) -> bytes:
    need(type(raw) is bytes and len(raw) == C20[0][2]
         and hashlib.sha256(raw).hexdigest() == C20[0][1],
         "require the entire unchanged, committed first-party C20 controller")
    need(raw.count(b"VERSION = 20\n") == 1
         and raw.count(b'corrected = corrected.replace(b"v19", b"v20")') == 1
         and raw.count(b'corrected = corrected.replace(b"V19", b"V20")') == 1
         and raw.count(b'corrected = corrected.replace('
                       b'b"VERSION = 19\\n", b"VERSION = 20\\n", 1)') == 1,
         "reject an ambiguous cumulative C20 first-party source transformer")
    corrected = raw.replace(b"c20", b"c21")
    corrected = corrected.replace(b"C20", b"C21")
    corrected = corrected.replace(b"v20", b"v21")
    corrected = corrected.replace(b"V20", b"V21")
    corrected = corrected.replace(b"VERSION = 20\n", b"VERSION = 21\n", 1)
    corrected = corrected.replace(b"VERSION = 20\\n", b"VERSION = 21\\n")
    injection_anchor = (
        b'    corrected = corrected.replace('
        b'b"VERSION = 19\\n", b"VERSION = 21\\n", 1)\n'
    )
    injection = injection_anchor + (
        b'    need(original.count(b"os.getrandom(12).hex()") == 1\n'
        b'         and original.count(b"os.getrandom(16).hex()") == 1\n'
        b'         and b"os.urandom(12).hex()" not in original\n'
        b'         and b"os.urandom(16).hex()" not in original,\n'
        b'         "require both real, unchanged vulnerable C20 randomness "\n'
        b'         "sites in the complete frozen first-party C19 controller")\n'
        b'    corrected = corrected.replace(\n'
        b'        b"os.getrandom(12).hex()", b"os.urandom(12).hex()", 1\n'
        b'    )\n'
        b'    corrected = corrected.replace(\n'
        b'        b"os.getrandom(16).hex()", b"os.urandom(16).hex()", 1\n'
        b'    )\n'
        b'    need(corrected.count(b"os.urandom(12).hex()") == 1\n'
        b'         and corrected.count(b"os.urandom(16).hex()") == 1\n'
        b'         and b"os.getrandom(12).hex()" not in corrected\n'
        b'         and b"os.getrandom(16).hex()" not in corrected,\n'
        b'         "replace both actual journal and private-root call sites "\n'
        b'         "with portable first-party operating-system CSPRNG")\n'
    )
    need(corrected.count(injection_anchor) == 1,
         "require one exact cumulative C21 entropy-correction insertion")
    corrected = corrected.replace(injection_anchor, injection, 1)
    need(b"VERSION = 21\n" in corrected
         and b"--authorize-first-party-native-build-v21" in corrected
         and SOURCE.encode("ascii") in corrected
         and PROTOCOL.encode("ascii") in corrected
         and CONTRACT.encode("ascii") in corrected
         and corrected.count(injection) == 1,
         "reject incomplete version 21 first-party controller or entropy fix")
    ast.parse(corrected, filename=SOURCE)
    return corrected


def bootstrap_overlay() -> types.ModuleType:
    clean_runtime()
    available = getattr(os, "urandom", None)
    need(callable(available),
         "require pinned Python's portable operating-system urandom CSPRNG")
    need(not hasattr(os, "getrandom"),
         "bind the actual portable-randomness capability of pinned CPython")
    previous = read_bootstrap(C20[0])
    transformed = derive_c21_wrapper(previous)
    wrapper = types.ModuleType("_rebar_c21_complete_first_party_c20_overlay")
    wrapper.__file__ = ROOT + "/" + SOURCE
    wrapper.__package__ = ""
    exec(compile(transformed, wrapper.__file__, "exec", dont_inherit=True),
         wrapper.__dict__)
    need(wrapper.SCHEMA == SCHEMA and wrapper.VERSION == VERSION
         and wrapper.SOURCE == SOURCE and wrapper.PROTOCOL == PROTOCOL
         and wrapper.CONTRACT == CONTRACT
         and wrapper.INSTALLED_SHA256 == INSTALLED_SHA256
         and wrapper.INSTALLED_BYTES == INSTALLED_BYTES
         and wrapper.INSTALLED_DEVICE == INSTALLED_DEVICE
         and wrapper.INSTALLED_INODE == INSTALLED_INODE
         and wrapper.INSTALLED_MODE == INSTALLED_MODE
         and wrapper.DERIVED_SHA256 == DERIVED_SHA256
         and wrapper.DERIVED_BYTES == DERIVED_BYTES,
         "reject incomplete first-party Match source or cumulative C21 identity")
    module = wrapper.bootstrap_overlay()
    need(module.SCHEMA == SCHEMA and module.VERSION == VERSION
         and module.SOURCE == SOURCE and module.PROTOCOL == PROTOCOL
         and module.CONTRACT == CONTRACT
         and module.BUILD_AUTHORIZATION
         == "--authorize-first-party-native-build-v21"
         and len(module.PHASES) == 2 and len(module.PROCESS_ROLES) == 7
         and module.EXPECTED_INSTALLED_NATIVE_SHA256 == INSTALLED_SHA256
         and module.DERIVED_SHA256 == DERIVED_SHA256
         and module.DERIVED_BYTES == DERIVED_BYTES,
         "retain the complete genuine two-phase first-party C21 builder")
    previous_bootstrap = module.bootstrap_wall
    previous_validate = module.validate_context
    previous_contract = module.contract_document
    previous_controls = module.source_controls
    previous_parse = module.parse_options
    previous_collect = module.collect_source

    def guarded_bootstrap() -> tuple:
        semantic, old, semantic_owners, base = previous_bootstrap()
        owners = base + C20 + (C20_FAILURE,)
        paths = tuple(item[0] for item in owners)
        module.need(len(paths) == len(frozenset(paths)),
                    "reject duplicate cumulative C21 source or failure owners")
        old.STATIC_OWNERS = owners
        old.OWNED_PATHS = frozenset(paths) | {SOURCE, PROTOCOL, CONTRACT}
        module.need(not any(
            path == module.CANONICAL_C[0]
            or path == module.CANONICAL_ADAPTER[0]
            or path.startswith("docs/evidence/")
            or "holdout" in path.lower()
            or "benchmark" in path.lower()
            or path.endswith((".so", ".gz", ".zip", ".tar", ".xz"))
            for path in old.OWNED_PATHS
        ), "source modes must physically deny native, candidate, private "
           "root, graph, archive, holdout, and timing owners")
        previous_wall = old.SourceWall

        class EntropyWall(previous_wall):
            def __enter__(self) -> object:
                active = super().__enter__()
                self.patch(os, "urandom", self.denied_callable(
                    "source-only operating-system entropy and private randomness"
                ))
                if hasattr(os, "getrandom"):
                    self.patch(os, "getrandom", self.denied_callable(
                        "source-only unavailable or actual entropy"
                    ))
                return active

        old.SourceWall = EntropyWall
        return semantic, old, semantic_owners, owners

    def guarded_validate(semantic: types.ModuleType, old: types.ModuleType,
                         semantic_owners: tuple, raw: dict,
                         producer: types.ModuleType) -> tuple:
        outcome = previous_validate(semantic, old, semantic_owners, raw, producer)
        c20 = document(producer, raw[C20[2][0]],
                       "complete committed first-party C20 source freeze")
        need(c20.get("schema")
             == "rebar-owned-c-original-match-semantics-source-build-v20-"
                "source-freeze"
             and c20.get("version") == 20
             and c20.get("source", {}).get("sha256") == C20[0][1]
             and c20.get("protocol", {}).get("sha256") == C20[1][1]
             and c20.get("candidate_correctness") == "NOT MEASURED"
             and c20.get("performance") == "NOT MEASURED"
             and c20.get("holdout") == "NOT OPENED"
             and c20.get("qualified_candidate_count") == 0,
             "preserve independently pushed C20 as a source freeze, "
             "never a successful native build")
        failure = validate_c20_failure(document(
            producer, raw[C20_FAILURE[0]],
            "genuinely pushed C20 dual-randomness actual failure",
        ), module)
        need(failure["installed_original_before"] == installed_identity()
             and failure["installed_original_after"] == installed_identity(),
             "preserve the actual unmodified C original across C20 failure")
        return outcome

    def guarded_contract(old: types.ModuleType, owners: tuple,
                         receipt: dict, previous_build: dict,
                         previous_root: dict,
                         source_sha: str, protocol_sha: str) -> dict:
        value = previous_contract(old, owners, receipt, previous_build,
                                  previous_root, source_sha, protocol_sha)
        value["preserved_c20_source_freeze"] = {
            "version": 20,
            "owners": [owner_record(item) for item in C20],
            "actual_native_build_status": "FAIL",
            "candidate_correctness": "NOT MEASURED",
        }
        value["actual_c20_portable_randomness_failure"] = {
            "receipt": owner_record(C20_FAILURE),
            "status": "FAIL",
            "failure_phase": "GENERATE PRIVATE ROOT RANDOMNESS AFTER "
                             "TOOLCHAIN AUTHENTICATION AND BEFORE "
                             "DIRECTORY CREATION",
            "error_type": "AttributeError",
            "error_message": "module 'os' has no attribute 'getrandom'",
            "pinned_build_authority_count": 26,
            "authenticated_toolchain_owner_count": 5,
            "failed_private_root_call": "os.getrandom(16)",
            "unreached_journal_call": "os.getrandom(12)",
            "actual_private_build_roots_created": 0,
            "actual_build_phases_completed": 0,
            "actual_compiler_process_count": 0,
            "actual_recovery_journals_created": 0,
            "actual_build_receipts_created": 0,
            "actual_root_receipts_created": 0,
            "original_native_before": installed_identity(),
            "original_native_after": installed_identity(),
            "failure_retried": False,
        }
        value["portable_first_party_entropy_correction"] = {
            "status": "BOTH CALL SITES STRUCTURALLY CORRECTED; "
                      "NO ACTUAL BUILD OR ENTROPY GENERATED",
            "exact_c20_source": owner_record(C20[0]),
            "complete_prior_controller_preserved": True,
            "external_package": "FORBIDDEN",
            "deterministic_entropy": "FORBIDDEN",
            "stdlib_re_engine": "FORBIDDEN",
            "fixed_private_root_call": "os.urandom(16)",
            "fixed_private_journal_call": "os.urandom(12)",
            "corrected_call_site_count": 2,
            "source_mode_entropy_requests": 0,
            "pinned_runtime_getrandom_available": False,
            "pinned_runtime_urandom_available": True,
            "candidate_correctness": "NOT MEASURED",
        }
        policy = value["future_actual_build_policy"]
        policy["portable_root_randomness"] = "os.urandom(16)"
        policy["portable_journal_randomness"] = "os.urandom(12)"
        policy["pushed_c20_failure_receipt_sha256"] = C20_FAILURE[1]
        policy["pushed_c20_source_sha256"] = C20[0][1]
        policy["pushed_c20_protocol_sha256"] = C20[1][1]
        policy["pushed_c20_contract_sha256"] = C20[2][1]
        policy["previous_authority_count"] = 26
        return value

    def guarded_controls(semantic: types.ModuleType, old: types.ModuleType,
                         wall: object, producer: types.ModuleType,
                         receipt: dict, raw: dict,
                         previous_build: dict, previous_root: dict) -> list:
        controls = previous_controls(
            semantic, old, wall, producer, receipt, raw,
            previous_build, previous_root,
        )
        actual_failure = document(producer, raw[C20_FAILURE[0]],
                                  "actual C20 portable entropy hostile control")
        validate_c20_failure(actual_failure, module)

        def forged_failure(key: str, replacement: object) -> None:
            forged = dict(actual_failure)
            forged[key] = replacement
            validate_c20_failure(forged, module)

        def forged_authority() -> None:
            forged = dict(actual_failure)
            values = dict(forged["independently_pinned_build_authority"])
            values["installed_original_sha256"] = "0" * 64
            forged["independently_pinned_build_authority"] = values
            validate_c20_failure(forged, module)

        def forged_original() -> None:
            forged = dict(actual_failure)
            forged["installed_original_after"] = dict(
                installed_identity(), inode=INSTALLED_INODE + 1,
            )
            validate_c20_failure(forged, module)

        def forged_entropy_site(size: int) -> None:
            raw19 = raw[C19[0][0]]
            original_call = ("os.getrandom(" + str(size) + ").hex()").encode()
            changed = raw19.replace(original_call,
                                    b"os.urandom(8).hex()", 1)
            wrapper.derive_c21_controller(changed)

        checks = (
            ("physically deny journal source-mode entropy",
             lambda: os.urandom(12)),
            ("physically deny root source-mode entropy",
             lambda: os.urandom(16)),
            ("reject changed exact journal entropy call",
             lambda: forged_entropy_site(12)),
            ("reject changed exact private-root entropy call",
             lambda: forged_entropy_site(16)),
            ("reject fake successful C20 build",
             lambda: forged_failure("status", "PASS")),
            ("reject invented C20 compiler process",
             lambda: forged_failure("actual_compiler_process_count", 1)),
            ("reject invented C20 private root",
             lambda: forged_failure("actual_private_build_roots_created", 1)),
            ("reject invented C20 recovery journal",
             lambda: forged_failure("actual_recovery_journals_created", 1)),
            ("reject invented C20 actual receipt",
             lambda: forged_failure("actual_build_receipts_created", 1)),
            ("reject forged portable-runtime getrandom availability",
             lambda: forged_failure("os_getrandom_available", True)),
            ("reject forged portable-runtime urandom absence",
             lambda: forged_failure("os_urandom_available", False)),
            ("reject fake pre-toolchain C20 failure stage",
             lambda: forged_failure("authenticated_toolchain_owner_count", 0)),
            ("reject changed genuine C20 authority count",
             lambda: forged_failure("independently_pinned_build_authority_count", 25)),
            ("reject changed genuine 26-pin authority mapping", forged_authority),
            ("reject changed original native after failed C20", forged_original),
            ("reject C20 failure replay", lambda: forged_failure("failure_retried", True)),
            ("reject synthetic installed-native access",
             lambda: os.open(
                 ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                 os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
            ("reject a source-only C21 compiler process",
             lambda: os.posix_spawn("/usr/bin/x86_64-linux-gnu-gcc-13",
                                    ["gcc", "--version"], {})),
            ("reject source-only native-root creation",
             lambda: os.mkdir(
                 "/tmp/rebar-phase2-c-original-match-semantics-v21-forbidden",
                 0o700)),
            ("reject source-only standard-library matcher",
             lambda: builtins.__import__("_sre")),
        )
        for label, action in checks:
            try:
                action()
            except Exception as error:
                need(type(error).__name__ in {
                    "BuildError", "CampaignError", "SourceError",
                    "C19Error", "C20Error", "C21Error", "ProducerError",
                }, "unexpected C21 portable-entropy hostile control: " + label)
                controls.append(label)
            else:
                raise C21Error("accepted a forbidden C21 source effect: " + label)
        need(len(controls) >= 114 and sum(wall.blocked.values()) >= 54,
             "require full C21 physically denied cryptographic entropy, "
             "native, root, compiler, and failure-forgery source gates")
        clean_runtime()
        return controls

    def guarded_parse(arguments: list) -> dict:
        required = {
            "--c20-source-sha256": C20[0][1],
            "--c20-protocol-sha256": C20[1][1],
            "--c20-contract-sha256": C20[2][1],
            "--c20-failure-receipt-sha256": C20_FAILURE[1],
        }
        build = bool(arguments) and arguments[0] == "--build"
        remaining = []
        supplied = {}
        index = 0
        while index < len(arguments):
            key = arguments[index]
            if key in required:
                need(build and key not in supplied
                     and index + 1 < len(arguments),
                     "reject C20-failure authority in source mode or "
                     "duplicate/incomplete C21 actual build pin")
                supplied[key] = exact_digest(arguments[index + 1], key)
                index += 2
            else:
                remaining.append(key)
                index += 1
        options = previous_parse(remaining)
        if build:
            need(supplied == required,
                 "independently pin all immutable C20 owners and genuine "
                 "portable-randomness failure before any actual C21 build")
            options.update(supplied)
        else:
            need(not supplied,
                 "source verification must never request actual build authority")
        return options

    def guarded_collect(options: dict) -> tuple:
        producer, frozen, derived, state = previous_collect(options)
        observed = state["observed"]
        observed.update({
            "actual_previous_c20_build_status": "FAIL",
            "actual_previous_c20_failure_receipt_sha256": C20_FAILURE[1],
            "actual_previous_c20_authenticated_toolchain_count": 5,
            "actual_previous_c20_compiler_process_count": 0,
            "actual_previous_c20_private_roots_created": 0,
            "actual_previous_c20_recovery_journals_created": 0,
            "actual_previous_c20_independent_authority_count": 26,
            "installed_original_sha256": INSTALLED_SHA256,
            "installed_original_bytes": INSTALLED_BYTES,
            "installed_original_device": INSTALLED_DEVICE,
            "installed_original_inode": INSTALLED_INODE,
            "installed_original_mode": INSTALLED_MODE,
            "portable_root_randomness": "os.urandom(16)",
            "portable_journal_randomness": "os.urandom(12)",
            "source_entropy_requests": 0,
        })
        return producer, frozen, derived, state

    module.bootstrap_wall = guarded_bootstrap
    module.validate_context = guarded_validate
    module.contract_document = guarded_contract
    module.source_controls = guarded_controls
    module.parse_options = guarded_parse
    module.collect_source = guarded_collect
    clean_runtime()
    return module


def main() -> int:
    try:
        clean_runtime()
        controller = bootstrap_overlay()
        return controller.main()
    except Exception as error:
        sys.stderr.write("C original Match source build V21: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
