#!/usr/bin/env python3
"""Freeze and independently reproduce six fully owned native regex families.

`--self-test` is entirely in-memory. `--verify-context` is strictly read-only.
Only an explicitly pinned `--build` can start an owned compiler or publish
new V4 evidence; this source freeze never authorizes that operation.
"""

from __future__ import annotations

import ast
import base64
import builtins
import copy
import ctypes
import gzip
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
SOURCE_RELATIVE = "tools/reproduce_owned_native_source_build_v4.py"
PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V4.md"
CONTRACT_RELATIVE = "oracle/phase2/native-source-build-v4.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-native-source-build-v4"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
WORK_PREFIX = "rebar-phase2-native-build-v4-"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48

PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_INCLUDE = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_GXX = "/usr/bin/x86_64-linux-gnu-g++-13"
PINNED_GFORTRAN = "/usr/bin/x86_64-linux-gnu-gfortran-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
PINNED_GO = "/home/dev-user/.openai/go/bin/go"
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"

SOURCE_OWNERS: dict[str, dict[str, tuple[str, int]]] = {
    "c": {
        "candidates/vm_candidate.py": ("b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707),
        "candidates/_vm_native.c": ("bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185),
    },
    "rust": {
        "candidates/rust_candidate.py": ("6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
        "candidates/rust/py_bridge.c": ("f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
        "candidates/rust/Cargo.toml": ("2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
        "candidates/rust/Cargo.lock": ("267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
        "candidates/rust/src/lib.rs": ("c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
        "candidates/rust/src/newline.rs": ("13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
        "candidates/rust/src/search.rs": ("4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
        "candidates/rust/src/stack.rs": ("5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
        "candidates/rust/src/unicode_tables.rs": ("f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    },
    "zig": {
        "candidates/zig_candidate.py": ("2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422),
        "candidates/zig/mini_regex.zig": ("a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915),
        "candidates/zig/py_bridge.c": ("67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026),
    },
    "cpp": {
        "candidates/cpp_candidate.py": ("8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5", 27488),
        "candidates/cpp/engine.hpp": ("66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9", 4089),
        "candidates/cpp/engine.cpp": ("a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5", 62813),
        "candidates/cpp/py_bridge.cpp": ("1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d", 25068),
    },
    "go": {
        "candidates/go_candidate.py": ("816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20", 31049),
        "candidates/go/go.mod": ("9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b", 44),
        "candidates/go/engine.go": ("6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192", 53782),
        "candidates/go/py_bridge.c": ("52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a", 39373),
    },
    "fortran": {
        "candidates/fortran_candidate.py": ("8db564771d38c0896a5207f1241a44463432dc5bf75dfcf657740d8bcfefd194", 26521),
        "candidates/fortran/engine.f90": ("5180da085487b9932e3f769e6baded6a8409a0b778890e6197aaea6dad1923a5", 85062),
        "candidates/fortran/py_bridge.c": ("8540b708de4819f1b3340c32e78eaf083c1cad35f016c0f7af33a27773694b0d", 26311),
    },
}

FAMILIES: dict[str, dict[str, Any]] = {
    "c": {"language": "C", "adapter_import": "_vm_native", "artifacts": {"extension": "_vm_native" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ()},
    "rust": {"language": "Rust", "adapter_import": "_rust_bridge", "artifacts": {"engine": "_rust_engine.so", "bridge": "_rust_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ("copyreg", "functools", "inspect")},
    "zig": {"language": "Zig", "adapter_import": "_zig_bridge", "artifacts": {"engine": "_zig_probe.so", "bridge": "_zig_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ()},
    "cpp": {"language": "C++", "adapter_import": "_cpp_bridge", "artifacts": {"bridge": "_cpp_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ("unicodedata",)},
    "go": {"language": "Go", "adapter_import": "_go_bridge", "artifacts": {"engine": "_go_engine.so", "bridge": "_go_bridge" + EXTENSION_SUFFIX, "generated_header": "_go_engine.h"}, "allowed_bridge_python_imports": ("unicodedata",)},
    "fortran": {"language": "Fortran", "adapter_import": "_fortran_bridge", "artifacts": {"engine": "_fortran_engine.so", "bridge": "_fortran_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ()},
}

GO_ENGINE_EXPORTS = frozenset({
    "rebar_go_compile", "rebar_go_release", "rebar_go_group_count",
    "rebar_go_flags", "rebar_go_name_count", "rebar_go_name_group",
    "rebar_go_name_length", "rebar_go_copy_name", "rebar_go_execute",
})
GO_STANDARD_IMPORTS = frozenset({
    "C", "fmt", "runtime/cgo", "strconv", "sync", "sync/atomic", "unsafe",
})
FORTRAN_ENGINE_EXPORTS = frozenset({
    "rebar_fortran_compile", "rebar_fortran_destroy",
    "rebar_fortran_group_count", "rebar_fortran_effective_flags",
    "rebar_fortran_name_count", "rebar_fortran_name_length",
    "rebar_fortran_name_group", "rebar_fortran_copy_name",
    "rebar_fortran_execute",
})
FORTRAN_BRIDGE_CALLBACK_EXPORTS = frozenset({
    "rebar_fortran_unicode_case_key",
    "rebar_fortran_locale_case_key",
    "rebar_fortran_locale_is_word",
})
RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group", "rebar_name_len",
})
ZIG_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures", "rebar_zig_collect_records",
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match", "rebar_zig_match_captures",
    "rebar_zig_match_captures_wide", "rebar_zig_match_inverted_wide",
    "rebar_zig_match_nonempty_wide", "rebar_zig_match_tree",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length", "rebar_zig_program_memory",
    "rebar_zig_program_size",
})
FORBIDDEN_MODULES = frozenset({
    "re", "_sre", "regex", "regexp", "re2", "pcre", "pcre2",
    "oniguruma", "hyperscan", "sre_compile", "sre_constants", "sre_parse",
})
FORBIDDEN_NATIVE_NAMES = frozenset({
    "regex", "regexp", "regcomp", "regexec", "regfree", "dlopen", "dlmopen",
    "dlsym", "dlvsym", "execv", "execve", "fork", "popen", "posix_spawn",
    "system", "execute_command_line", "get_environment_variable",
    "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String",
    "Py_CompileString", "PyEval_EvalCode",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "regexp_",
    "sre_", "_sre", "PyInit__sre", "PyRun_", "PyEval_Eval",
)
FAMILY_SYSTEM_LIBRARIES: dict[str, frozenset[str]] = {
    "c": frozenset({"libc.so.6"}),
    "rust": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2"}),
    "zig": frozenset({"libc.so.6", "libm.so.6", "ld-linux-x86-64.so.2"}),
    "cpp": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "libstdc++.so.6", "ld-linux-x86-64.so.2"}),
    "go": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2"}),
    "fortran": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "libgfortran.so.5", "libquadmath.so.0", "ld-linux-x86-64.so.2"}),
}

EXPECTED_TOOLCHAINS: dict[str, tuple[str, str, int, str, bool]] = {
    "python": (PINNED_PYTHON, "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016", 32387816, "CPython 3.14.6", True),
    "python_header": (PYTHON_INCLUDE + "/Python.h", "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f", 4399, "CPython 3.14.6", False),
    "python_patchlevel": (PYTHON_INCLUDE + "/patchlevel.h", "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95", 1773, "CPython 3.14.6", False),
    "gcc": (PINNED_GCC, "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, "GCC 13", True),
    "gxx": (PINNED_GXX, "1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769", 1027128, "G++ 13", True),
    "gfortran": (PINNED_GFORTRAN, "142861efc95f49e33705852027dae8c2e5382fd1155fcec6116ef973f25d8f84", 1027128, "GNU Fortran 13", True),
    "readelf": (PINNED_READELF, "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, "GNU readelf", True),
    "go": (PINNED_GO, "d68b7abbc40d0844f673f6cf06ae3cded225c50437c6454fa37ef178d079fe65", 15434598, "go1.26.3 linux/amd64", True),
    "rustc": (PINNED_RUSTC, "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6", 644784, "rustc 1.95.0", True),
    "cargo": (PINNED_CARGO, "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66", 42185192, "cargo 1.95.0", True),
    "rust_driver": (RUST_TOOLCHAIN + "/lib/librustc_driver-6108105cd7e839cf.so", "ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484", 153621360, "rustc 1.95.0 compiler driver", False),
    "zig_archive": ("/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz", "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00", 55478392, "official Zig 0.16.0 x86_64-linux", False),
    "zig": (PINNED_ZIG, "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c", 172641672, "official Zig 0.16.0", True),
}

EXPECTED_SUPPORT: dict[str, tuple[str, str, int]] = {
    "objective": ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    "p0_manifest": ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632),
    "p0_protocol": ("oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392),
    "p0_verifier": ("tools/verify_p0_completeness_v1.py", "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c", 118040),
    "independence_protocol_v1": ("oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md", "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292", 7127),
    "independence_auditor_v1": ("tools/audit_candidate_independence_v1.py", "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5", 75793),
    "build_recorder_v2": ("tools/reproduce_phase2_native_builds_v2.py", "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796", 136677),
    "build_protocol_v2": ("oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md", "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603", 13032),
    "build_recorder_v3": ("tools/reproduce_phase2_native_builds_v3.py", "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f", 175029),
    "build_protocol_v3": ("oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md", "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3", 7979),
    "official_zig_lock": ("toolchains/zig-0.16.0.lock.json", "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd", 628),
}

EXPECTED_HISTORY: dict[str, dict[str, Any]] = {
    "c": {"family": "c", "build_status": "PASS", "archive_path": "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2.json.gz", "archive_sha256": "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878", "archive_bytes": 16016, "uncompressed_sha256": "0d0a67a3c8ebba83806ba3b9beaee39e154f9d0483f0e39aac6bb04ecbfc598a", "uncompressed_bytes": 169716, "receipt_path": "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2-publication-receipt.json", "receipt_sha256": "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24", "receipt_bytes": 1639, "process_count": 8},
    "rust": {"family": "rust", "build_status": "PASS", "archive_path": "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2.json.gz", "archive_sha256": "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d", "archive_bytes": 33741, "uncompressed_sha256": "389a833d6a3ce6c7aed3216759278d97d8d02dd901f758815e002f7a0031d4ec", "uncompressed_bytes": 279925, "receipt_path": "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2-publication-receipt.json", "receipt_sha256": "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e", "receipt_bytes": 2346, "process_count": 16},
    "zig": {"family": "zig", "build_status": "FAIL", "archive_path": "oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures.json.gz", "archive_sha256": "dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e", "archive_bytes": 19556, "uncompressed_sha256": "f6ea1eb57d9ceb23c6dc5d4f291c4eb300768460a658d97828b7ce0095c53652", "uncompressed_bytes": 188479, "receipt_path": "oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json", "receipt_sha256": "97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a", "receipt_bytes": 1766, "process_count": 15},
}

EXPECTED_BUILD_POLICY: dict[str, Any] = {
    "phase_names": ["reference-a", "reference-b"],
    "private_root_prefix": "/tmp/" + WORK_PREFIX,
    "private_root_mode": "0700",
    "phase_source_cache_target_output_and_process_identity": "DISTINCT",
    "all_phase_outputs": "BYTE IDENTICAL OR PRESERVE FAILURE",
    "argv_environment_working_directory_stdout_stderr_and_pid": "COMPLETE AND AUTHENTICATED",
    "elf_dynamic_symbols_and_versions": "COMPLETE AND AUTHENTICATED",
    "bridge_runpath": "$ORIGIN",
    "rpath": "FORBIDDEN",
    "zig_engine_strip_flag": "-fstrip",
    "go_build_mode": "c-shared",
    "go_generated_header": "FRESH, PHASE-OWNED, AUTHENTICATED, FORCED WITH -include, AND REPRODUCIBLE",
    "rust_package_count": 1,
    "rust_external_package_count": 0,
    "go_module_count": 1,
    "go_external_package_count": 0,
    "network_requests": 0,
    "external_regular_expression_packages": 0,
    "cross_family_matching_dependencies": 0,
    "stdlib_matching_delegation": 0,
    "fallback": "FORBIDDEN",
    "prebuilt_artifact": "FORBIDDEN",
    "evidence_creation": "BOUNDED, EXCLUSIVE, CANONICAL, AND SYNCHRONIZED",
}

EXPECTED_PHASE_BOUNDARY: dict[str, Any] = {
    "native_builds_started": 0, "candidate_processes_started": 0,
    "reference_processes_started": 0, "candidate_imports": 0,
    "native_libraries_loaded": 0, "hidden_cases_read": 0,
    "final_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0,
    "timing_trials_run": 0, "candidate_correctness": "NOT MEASURED",
    "subinterpreter_isolation": "NOT MEASURED",
    "undefined_behavior": "NOT MEASURED", "performance": "NOT MEASURED",
    "memory": "NOT MEASURED", "holdout": "NOT OPENED",
    "winner_selected": False,
}


class BuildError(Exception):
    """A frozen source, provenance, or build invariant failed closed."""


class SourceOnlyError(BuildError):
    """A synthetic control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("a finite, complete canonical JSON record is required") from error


def checked_digest(value: Any, description: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(ch in "0123456789abcdef" for ch in value),
            "an exact lowercase SHA-256 is required: " + description)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one owned C, Rust, Zig, C++, Go, or Fortran family")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512
            and "\\" not in value and "\x00" not in value
            and not value.startswith("/"),
            "a bounded, non-absolute repository-relative path is required")
    require(all(part not in ("", ".", "..") for part in value.split("/")),
            "reject source traversal, empty components, and alternate roots")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value)
            and "--" not in value and not value.endswith("-"),
            "supply one fresh lowercase, non-overwriting V4 build label")
    return value


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    found: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in found,
                "reject duplicated or non-string JSON object keys")
        found[key] = value
    return found


def reject_json_constant(value: str) -> Any:
    raise BuildError("reject non-finite JSON: " + value)


def decode_json(raw: Any, *, canonical_required: bool = False) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "complete bounded UTF-8 JSON is required")
    try:
        value = json.loads(raw.decode("utf-8"),
                           object_pairs_hook=unique_json_pairs,
                           parse_constant=reject_json_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise BuildError("reject truncated, duplicated, or invalid JSON") from error
    require(type(value) is dict, "a top-level JSON object is mandatory")
    if canonical_required:
        require(canonical(value) == raw, "an exact canonical JSON encoding changed")
    return value


def expected_oracle() -> dict[str, Any]:
    return {
        "implementation": "CPython", "version": "3.14.6",
        "suite_count": 13, "case_execution_count": 31237,
        "manifest_path": EXPECTED_SUPPORT["p0_manifest"][0],
        "manifest_sha256": EXPECTED_SUPPORT["p0_manifest"][1],
    }


def expected_contract() -> dict[str, Any]:
    families = []
    for family, specification in FAMILIES.items():
        families.append({
            "id": family, "language": specification["language"],
            "adapter_import": specification["adapter_import"],
            "artifacts": dict(specification["artifacts"]),
            "allowed_bridge_python_imports": list(
                specification["allowed_bridge_python_imports"]),
            "owners": [
                {"path": path, "sha256": digest, "bytes": size}
                for path, (digest, size) in SOURCE_OWNERS[family].items()
            ],
        })
    toolchains = [
        {"id": key, "path": path, "sha256": digest, "bytes": size,
         "version": version, "executable": executable}
        for key, (path, digest, size, version, executable)
        in EXPECTED_TOOLCHAINS.items()
    ]
    support = [
        {"id": key, "path": path, "sha256": digest, "bytes": size}
        for key, (path, digest, size) in EXPECTED_SUPPORT.items()
    ]
    return {
        "schema": CONTRACT_SCHEMA, "version": 4,
        "phase": "SOURCE FREEZE; NO BUILD AUTHORIZED",
        "oracle": expected_oracle(), "family_count": 6,
        "qualified_candidate_count": 0, "families": families,
        "toolchains": toolchains, "pinned_support": support,
        "historical_v2": [copy.deepcopy(item) for item in EXPECTED_HISTORY.values()],
        "build_policy": copy.deepcopy(EXPECTED_BUILD_POLICY),
        "phase_boundary": copy.deepcopy(EXPECTED_PHASE_BOUNDARY),
    }


def validate_contract(value: Any) -> dict[str, Any]:
    require(type(value) is dict and value == expected_contract(),
            "the complete six-family, 25-owner frozen V4 source contract changed")
    all_owners = [path for owners in SOURCE_OWNERS.values() for path in owners]
    require(len(all_owners) == 25 and len(set(all_owners)) == 25,
            "owned semantic source closures must be complete and pairwise disjoint")
    for path in all_owners:
        checked_relative(path)
    for specifications in SOURCE_OWNERS.values():
        for path, (digest, size) in specifications.items():
            checked_digest(digest, path)
            require(type(size) is int and 0 < size <= MAX_SOURCE_BYTES,
                    "every owned source requires its exact bounded byte count")
    return value


def validate_phase1_manifest(raw: bytes) -> dict[str, Any]:
    value = decode_json(raw, canonical_required=True)
    suites, phase, guards = value.get("suites"), value.get("phase_gate"), value.get("audit_boundaries")
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and value.get("version") == 1,
            "the complete frozen CPython correctness oracle was substituted")
    require(type(suites) is list and len(suites) == 13
            and all(type(item) is dict for item in suites)
            and sum(item.get("case_execution_count", 0) for item in suites) == 31237
            and all(item.get("baseline", {}).get("status") == "PASS" for item in suites),
            "all 13 frozen suites and 31,237 actual reference passes are required")
    require(type(phase) is dict and phase.get("status") == "PASS"
            and phase.get("all_obligations_mapped") is True
            and phase.get("blockers") == []
            and phase.get("candidate_evaluation_authorized") is False
            and phase.get("final_holdout_authorized") is False,
            "reject incomplete correctness or unauthorized candidate/holdout access")
    require(type(guards) is dict and guards.get("hidden_cases_read") == 0
            and guards.get("final_cases_read") == 0
            and guards.get("timing_trials_run") == 0
            and guards.get("candidate_qualified") is False,
            "the source freeze may not inherit holdout, timing, or candidate results")
    denominator = value.get("denominator")
    require(type(denominator) is dict
            and denominator.get("final_required_case_execution_denominator") == 31237
            and denominator.get("available_frozen_vector_case_executions") == 31237,
            "the exact frozen 31,237-case denominator changed")
    return {
        "status": "PASS", "suite_count": 13,
        "case_execution_count": 31237,
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified_count": 0,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
    }


def validate_zig_lock(raw: bytes) -> dict[str, Any]:
    actual = decode_json(raw)
    expected = {
        "schema": "rebar-official-language-toolchain-v1", "language": "Zig",
        "version": "0.16.0", "release_channel": "stable",
        "platform": "x86_64-linux",
        "official_release_index": "https://ziglang.org/download/index.json",
        "archive_url": "https://ziglang.org/download/0.16.0/zig-x86_64-linux-0.16.0.tar.xz",
        "archive_sha256": EXPECTED_TOOLCHAINS["zig_archive"][1],
        "archive_bytes": EXPECTED_TOOLCHAINS["zig_archive"][2],
        "archive_root": "zig-x86_64-linux-0.16.0",
        "compiler_relative_path": "zig-x86_64-linux-0.16.0/zig",
        "compiler_sha256": EXPECTED_TOOLCHAINS["zig"][1],
    }
    require(actual == expected, "the complete official offline Zig 0.16.0 lock changed")
    return {"language": "Zig", "version": "0.16.0",
            "archive_sha256": expected["archive_sha256"],
            "compiler_sha256": expected["compiler_sha256"],
            "network_requests": 0, "path_lookup_used": False}


def authenticate_file(
    path: Path, *, expected: str | None, maximum: int,
    exact_size: int | None = None, capture: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    require(isinstance(path, Path) and path.is_absolute()
            and type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES
            and type(capture) is bool,
            "authenticate only an absolute bounded regular file")
    if expected is not None:
        checked_digest(expected, str(path))
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "a frozen file requires its exact bounded size")
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "the frozen owner is not the exact bounded regular file")
        digest, retained, count = hashlib.sha256(), bytearray() if capture else None, 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            count += len(block)
            require(count <= maximum, "the authenticated owner grew during reading")
            digest.update(block)
            if retained is not None:
                retained.extend(block)
        after, visible = os.fstat(descriptor), os.lstat(str(path))
        require(count == before.st_size == after.st_size
                and (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_ctime_ns)
                and stat.S_ISREG(visible.st_mode)
                and (visible.st_dev, visible.st_ino, visible.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "reject a symlink, replacement, mutable owner, or truncated source")
        observed = digest.hexdigest()
        require(expected is None or observed == expected,
                "a pinned source, toolchain, protocol, or record changed: " + str(path))
        return ({"path": str(path), "sha256": observed, "size_bytes": count,
                 "device": after.st_dev, "inode": after.st_ino,
                 "executable": bool(after.st_mode & 0o111)},
                bytes(retained) if retained is not None else None)
    finally:
        os.close(descriptor)


def native_tokens(raw: Any, *, fortran: bool = False) -> list[tuple[str, str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "complete bounded native source is required")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("the complete native source must be valid UTF-8") from error
    tokens: list[tuple[str, str]] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if source.startswith("//", index) or (fortran and char == "!"):
            end = source.find("\n", index + (2 if source.startswith("//", index) else 1))
            index = len(source) if end < 0 else end + 1
            continue
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            require(end >= 0, "reject an unterminated native comment")
            index = end + 2
            continue
        if char == "'" and not fortran and index + 1 < len(source) \
                and (source[index + 1] == "_" or source[index + 1].isalpha()):
            end = index + 2
            while end < len(source) and (source[end] == "_" or source[end].isalnum()):
                end += 1
            if end >= len(source) or source[end] != "'":
                tokens.append(("punctuation", char))
                index += 1
                continue
        if char in "\"'":
            quote, start = char, index + 1
            index += 1
            while index < len(source):
                if source[index] == quote:
                    if fortran and index + 1 < len(source) and source[index + 1] == quote:
                        index += 2
                        continue
                    break
                if source[index] == "\\" and not fortran:
                    index += 1
                index += 1
            require(index < len(source), "reject an unterminated native string")
            tokens.append(("string", source[start:index]))
            index += 1
            continue
        if char == "_" or char.isalpha():
            start = index
            index += 1
            while index < len(source) and (source[index] == "_" or source[index].isalnum()):
                index += 1
            name = source[start:index]
            tokens.append(("identifier", name.lower() if fortran else name))
            continue
        tokens.append(("punctuation", char))
        index += 1
    return tokens


def audit_native_source(raw: bytes, *, family: str, location: str) -> dict[str, Any]:
    family = checked_family(family)
    checked_relative(location)
    tokens = native_tokens(raw, fortran=location.endswith(".f90"))
    identifiers = {value for kind, value in tokens if kind == "identifier"}
    for name in identifiers:
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(prefix) for prefix in FORBIDDEN_NATIVE_PREFIXES),
                "a native source delegates to an external matcher or process: " + name)
    imports: list[str] = []
    go_imports: list[str] = []
    for index, (kind, value) in enumerate(tokens):
        if (family == "go" and location == "candidates/go/engine.go"
                and kind == "identifier" and value == "import"):
            require(index + 1 < len(tokens), "a complete Go import declaration is required")
            next_kind, next_value = tokens[index + 1]
            if next_kind == "string":
                go_imports.append(next_value)
            else:
                require((next_kind, next_value) == ("punctuation", "("),
                        "reject a computed or uninspectable Go package import")
                position = index + 2
                while position < len(tokens) and tokens[position] != ("punctuation", ")"):
                    entry_kind, entry_value = tokens[position]
                    require(entry_kind == "string",
                            "reject aliased, computed, or disguised Go package imports")
                    go_imports.append(entry_value)
                    position += 1
                require(position < len(tokens), "reject an unterminated Go import group")
        if kind == "identifier" and value == "import" \
                and index > 0 and tokens[index - 1] == ("punctuation", "@"):
            require(index + 2 < len(tokens) and tokens[index + 1] == ("punctuation", "(")
                    and tokens[index + 2][0] == "string",
                    "reject a computed Zig package import")
            imported = tokens[index + 2][1]
            require(imported == "std",
                    "reject an external or regular-expression Zig package import")
        if kind == "identifier" and value == "PyImport_ImportModule":
            require(index + 2 < len(tokens) and tokens[index + 1] == ("punctuation", "(")
                    and tokens[index + 2][0] == "string",
                    "reject a computed native Python support import")
            target = tokens[index + 2][1]
            expected_bridge = {
                "rust": "candidates/rust/py_bridge.c",
                "cpp": "candidates/cpp/py_bridge.cpp",
                "go": "candidates/go/py_bridge.c",
            }.get(family)
            require(location == expected_bridge
                    and target in FAMILIES[family]["allowed_bridge_python_imports"],
                    "reject a standard-regex, cross-family, or undeclared support import")
            imports.append(target)
    required = {
        "candidates/_vm_native.c": "PyInit__vm_native",
        "candidates/rust/py_bridge.c": "PyInit__rust_bridge",
        "candidates/rust/src/lib.rs": "rebar_compile",
        "candidates/zig/mini_regex.zig": "rebar_zig_compile",
        "candidates/zig/py_bridge.c": "PyInit__zig_bridge",
        "candidates/cpp/engine.hpp": "rebar_cpp",
        "candidates/cpp/engine.cpp": "rebar_cpp",
        "candidates/cpp/py_bridge.cpp": "PyInit__cpp_bridge",
        "candidates/go/engine.go": "rebar_go_compile",
        "candidates/go/py_bridge.c": "PyInit__go_bridge",
        "candidates/fortran/engine.f90": "rebar_fortran_compile",
        "candidates/fortran/py_bridge.c": "PyInit__fortran_bridge",
    }.get(location)
    if required is not None:
        require(required in identifiers,
                "an independently owned native entry point is missing: " + required)
    if location == "candidates/go/engine.go":
        require(len(go_imports) == len(GO_STANDARD_IMPORTS)
                and len(set(go_imports)) == len(go_imports)
                and set(go_imports) == GO_STANDARD_IMPORTS,
                "reject a Go regexp, regexp/syntax, package, plugin, or foreign module")
        source = raw.decode("utf-8")
        exports = [line.strip()[len("//export "):]
                   for line in source.splitlines()
                   if line.strip().startswith("//export ")]
        require(len(exports) == len(GO_ENGINE_EXPORTS)
                and len(set(exports)) == len(exports)
                and set(exports) == GO_ENGINE_EXPORTS,
                "all nine exact owned Go c-shared exports are required")
    return {"path": location, "native_identifier_count": len(identifiers),
            "native_literal_imports": sorted(imports),
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0}


def audit_python_source(raw: bytes, *, family: str, location: str) -> dict[str, Any]:
    family = checked_family(family)
    checked_relative(location)
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "the complete owned Python adapter is mandatory")
    try:
        source = raw.decode("utf-8")
        document = ast.parse(source, filename=location, mode="exec")
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise BuildError("an independently owned Python adapter is invalid") from error
    own_bridge = FAMILIES[family]["adapter_import"]
    imports: set[str] = set()
    saw_own_bridge = False
    native_loaders = 0
    for node in ast.walk(document):
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(alias.name.split(".", 1)[0] not in FORBIDDEN_MODULES,
                        "reject a Python standard or external matcher import")
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            require(module.split(".", 1)[0] not in FORBIDDEN_MODULES,
                    "reject an imported standard or external matcher")
            imports.add(module)
            if module == "candidates":
                for alias in node.names:
                    require(alias.name == own_bridge,
                            "a Python adapter imports another candidate's engine")
                    saw_own_bridge = True
            elif module.startswith("candidates."):
                raise BuildError("reject a computed or cross-family candidate import")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                require(func.id not in {"__import__", "eval", "exec"},
                        "reject a computed candidate import or evaluator")
            elif isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    pair = (func.value.id, func.attr)
                    require(pair not in {
                        ("importlib", "import_module"), ("importlib", "__import__"),
                        ("os", "system"), ("os", "popen"),
                        ("subprocess", "run"), ("subprocess", "Popen"),
                    }, "reject an indirect import, process, or matching engine")
                    if pair == ("ctypes", "CDLL"):
                        native_loaders += 1
                        require(family == "zig", "only the exact owned Zig loader is permitted")
                require(func.attr != "find_library", "reject an unpinned native loader")
        elif isinstance(node, ast.Constant) and node.value == "__import__":
            raise BuildError("reject a disguised dynamic importer")
    require(saw_own_bridge, "the adapter must import exactly its own native bridge")
    require(native_loaders == (1 if family == "zig" else 0),
            "reject an omitted, duplicate, or foreign native library loader")
    if family == "zig":
        require("_zig_probe.so" in source and "os.path.dirname(__file__)" in source,
                "the Zig loader must name its own adjacent, phase-built engine")
    return {"path": location, "imports": sorted(imports),
            "own_native_bridge": own_bridge,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0}


def validate_cargo_closure(manifest_raw: bytes, lock_raw: bytes) -> dict[str, Any]:
    require(type(manifest_raw) is bytes and type(lock_raw) is bytes,
            "both complete owned Rust package files are mandatory")
    try:
        manifest = tomllib.loads(manifest_raw.decode("utf-8"))
        lock = tomllib.loads(lock_raw.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
        raise BuildError("reject an invalid dependency-free Rust source closure") from error
    require(set(manifest) == {"package", "lib", "profile"}
            and manifest["package"] == {
                "name": "rebar-rust-continuation", "version": "0.1.0",
                "edition": "2024", "rust-version": "1.85", "publish": False,
            }
            and manifest["lib"] == {"crate-type": ["cdylib"]}
            and manifest["profile"] == {"release": {
                "opt-level": 3, "lto": True, "codegen-units": 1,
                "panic": "abort",
            }}, "reject third-party Rust crates, build hooks, or changed compilation")
    require(lock == {"version": 4, "package": [
        {"name": "rebar-rust-continuation", "version": "0.1.0"},
    ]}, "the owned Rust lock contains a foreign dependency")
    return {"package_count": 1, "external_package_count": 0,
            "network_requests": 0, "offline": True}


def validate_go_module(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and raw == b"module rebar.local/candidates/go\n\ngo 1.26.0\n",
            "the Go module must be exactly one dependency-free first-party package")
    return {"module": "rebar.local/candidates/go", "go_version": "1.26.0",
            "module_count": 1, "external_package_count": 0,
            "network_requests": 0, "offline": True}


def checked_source_pins(family: str, values: Any) -> dict[str, str]:
    family = checked_family(family)
    owners = SOURCE_OWNERS[family]
    require(type(values) is list and len(values) == len(owners),
            "pin every independently owned family source exactly once")
    observed: dict[str, str] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "source pins must be exactly RELATIVE/PATH=SHA256")
        path, digest = item.split("=", 1)
        checked_relative(path)
        require(path in owners and path not in observed,
                "reject a missing, repeated, foreign, or sibling source owner")
        require(checked_digest(digest, path) == owners[path][0],
                "a source pin must equal the exact frozen V4 source contract")
        observed[path] = digest
    require(set(observed) == set(owners), "the whole exact family source closure is required")
    return dict(sorted(observed.items()))


def checked_workdir(value: Any, family: str) -> str:
    family = checked_family(family)
    require(type(value) is str and value.startswith("/tmp/" + WORK_PREFIX + family + "-")
            and "\\" not in value and "\x00" not in value
            and value == value.rstrip("/")
            and len(value.split("/")) == 3,
            "reject a broad, reused, redirected, or cross-family private build root")
    require(all(part not in ("", ".", "..") for part in value.split("/")[1:]),
            "reject a traversing private build root")
    return value


def phase_paths(workdir: str, family: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir, family)
    require(phase in ("reference-a", "reference-b"),
            "exactly two distinct fresh source-build phases are mandatory")
    base = Path(workdir) / phase
    source, native = base / "source", base / "native"
    result = {
        "base": base, "source": source, "native": native,
        "temporary": base / "temporary", "target": base / "target",
        "cargo_home": base / "cargo-home",
        "zig_local_cache": base / "zig-local-cache",
        "zig_global_cache": base / "zig-global-cache",
        "go_build_cache": base / "go-build-cache",
        "go_module_cache": base / "go-module-cache",
        "fortran_modules": base / "fortran-modules",
        "rust_manifest": source / "candidates/rust/Cargo.toml",
        "rust_target_engine": base / "target/release/librebar_rust_continuation.so",
        "go_module_directory": source / "candidates/go",
    }
    for kind, filename in FAMILIES[family]["artifacts"].items():
        result["artifact_" + kind] = native / filename
    return result


def reproducible_prefix_flags(workdir: str, family: str) -> tuple[list[str], str]:
    flags, rust = [], []
    for phase in ("reference-a", "reference-b"):
        source = str(phase_paths(workdir, family, phase)["source"])
        flags.append("-ffile-prefix-map=" + source + "=/rebar-phase2-v4-owned-source")
        rust.append("--remap-path-prefix=" + source + "=/rebar-phase2-v4-owned-source")
    if family == "rust":
        rust.append("-Clink-arg=-Wl,-soname,_rust_engine.so")
    return flags, " ".join(rust)


def build_environment(workdir: str, family: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, family, phase)
    _, rustflags = reproducible_prefix_flags(workdir, family)
    environment = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C",
        "TZ": "UTC", "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
    }
    if family == "rust":
        environment.update({
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "CARGO_HOME": str(paths["cargo_home"]),
            "CARGO_NET_OFFLINE": "true", "CARGO_INCREMENTAL": "0",
            "CARGO_BUILD_JOBS": "1", "RUSTC": PINNED_RUSTC,
            "RUSTFLAGS": rustflags,
        })
    elif family == "zig":
        environment.update({
            "ZIG_LOCAL_CACHE_DIR": str(paths["zig_local_cache"]),
            "ZIG_GLOBAL_CACHE_DIR": str(paths["zig_global_cache"]),
        })
    elif family == "go":
        environment.update({
            "GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off",
            "GOENV": "off", "GOTOOLCHAIN": "local", "CGO_ENABLED": "1",
            "CC": PINNED_GCC, "GOCACHE": str(paths["go_build_cache"]),
            "GOMODCACHE": str(paths["go_module_cache"]),
            "GOFLAGS": "-mod=readonly",
        })
    return environment


def planned_commands(workdir: str, family: str, phase: str) -> dict[str, list[str]]:
    family = checked_family(family)
    paths = phase_paths(workdir, family, phase)
    prefix, _ = reproducible_prefix_flags(workdir, family)
    commands: dict[str, list[str]] = {"readelf_version": [PINNED_READELF, "--version"]}
    if family in {"c", "rust", "zig", "go", "fortran"}:
        commands["gcc_version"] = [PINNED_GCC, "--version"]
    if family == "c":
        commands["build_c_extension"] = [
            PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/_vm_native.c"),
            "-o", str(paths["artifact_extension"]),
        ]
    elif family == "rust":
        commands["rustc_version"] = [PINNED_RUSTC, "--version", "--verbose"]
        commands["cargo_version"] = [PINNED_CARGO, "--version"]
        commands["build_rust_engine"] = [
            PINNED_CARGO, "build", "--manifest-path", str(paths["rust_manifest"]),
            "--release", "--locked", "--offline", "--frozen",
            "--target-dir", str(paths["target"]),
        ]
        commands["build_rust_bridge"] = [
            PINNED_GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
            "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/rust/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_rust_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    elif family == "zig":
        commands["zig_version"] = [PINNED_ZIG, "version"]
        commands["build_zig_engine"] = [
            PINNED_ZIG, "build-lib",
            str(paths["source"] / "candidates/zig/mini_regex.zig"),
            "-dynamic", "-lc", "-O", "ReleaseFast", "-fstrip",
            "-fallow-shlib-undefined", "-fsoname=_zig_probe.so",
            "--cache-dir", str(paths["zig_local_cache"]),
            "--global-cache-dir", str(paths["zig_global_cache"]),
            "-femit-bin=" + str(paths["artifact_engine"]),
        ]
        commands["build_zig_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/zig/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_zig_probe.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    elif family == "cpp":
        commands["gxx_version"] = [PINNED_GXX, "--version"]
        commands["build_cpp_bridge"] = [
            PINNED_GXX, "-std=c++20", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            "-I" + str(paths["source"] / "candidates/cpp"),
            str(paths["source"] / "candidates/cpp/engine.cpp"),
            str(paths["source"] / "candidates/cpp/py_bridge.cpp"),
            "-o", str(paths["artifact_bridge"]),
        ]
    elif family == "go":
        commands["go_version"] = [PINNED_GO, "version"]
        commands["build_go_engine"] = [
            PINNED_GO, "build", "-buildmode=c-shared", "-trimpath",
            "-buildvcs=false", "-ldflags=-buildid=",
            "-o", str(paths["artifact_engine"]), ".",
        ]
        commands["build_go_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE, "-I" + str(paths["native"]),
            "-include", str(paths["artifact_generated_header"]),
            str(paths["source"] / "candidates/go/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_go_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    else:
        commands["gfortran_version"] = [PINNED_GFORTRAN, "--version"]
        commands["build_fortran_engine"] = [
            PINNED_GFORTRAN, "-shared", "-fPIC", "-O3",
            "-ffree-line-length-none", "-Wl,--build-id=sha1",
            "-Wl,-soname,_fortran_engine.so", *prefix,
            "-J" + str(paths["fortran_modules"]),
            str(paths["source"] / "candidates/fortran/engine.f90"),
            "-o", str(paths["artifact_engine"]),
        ]
        commands["build_fortran_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/fortran/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_fortran_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    for kind in FAMILIES[family]["artifacts"]:
        if kind == "generated_header":
            continue
        path = paths["artifact_" + kind]
        commands[kind + "_dynamic"] = [PINNED_READELF, "--dynamic", "--wide", str(path)]
        commands[kind + "_symbols"] = [PINNED_READELF, "--dyn-syms", "--wide", str(path)]
    return commands


def checked_command(name: Any, argv: Any, workdir: str, family: str, phase: str) -> list[str]:
    commands = planned_commands(workdir, family, phase)
    require(type(name) is str and name in commands and type(argv) is list
            and all(type(value) is str and "\x00" not in value for value in argv)
            and argv == commands[name],
            "reject an abbreviated, shell-based, unpinned, networked, or modified command")
    require(argv[0] in {PINNED_GCC, PINNED_GXX, PINNED_GFORTRAN,
                         PINNED_READELF, PINNED_GO, PINNED_RUSTC,
                         PINNED_CARGO, PINNED_ZIG},
            "only an exact authenticated compiler or ELF inspector may run")
    return list(argv)


def sanitized(value: str, workdir: str, family: str) -> str:
    return value.replace(checked_workdir(workdir, family), "<FRESH_PRIVATE_TMP>")


def parse_elf_dynamic(raw: Any) -> dict[str, list[str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "complete bounded dynamic-library evidence is mandatory")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("dynamic-library evidence is not valid UTF-8") from error
    found: dict[str, list[str]] = {"needed": [], "runpath": [], "rpath": [], "soname": []}
    markers = {"(NEEDED)": "needed", "(RUNPATH)": "runpath",
               "(RPATH)": "rpath", "(SONAME)": "soname"}
    for line in source.splitlines():
        for marker, key in markers.items():
            if marker in line:
                start, end = line.find("["), line.find("]", line.find("[") + 1)
                require(start >= 0 and end > start + 1,
                        "a native dependency lacks its exact complete value")
                value = line[start + 1:end]
                require("\x00" not in value, "reject a malformed native dependency")
                found[key].append(value)
    for key, values in found.items():
        require(len(values) == len(set(values)),
                "reject a duplicate dynamic-library entry: " + key)
    return found


def checked_symbol_name(value: Any) -> tuple[str, str | None, bool]:
    require(type(value) is str and 0 < len(value) <= 1024,
            "a complete bounded versioned ELF symbol is mandatory")
    parts = value.split("@")
    require(1 <= len(parts) <= 3, "reject invalid or concealed GNU symbol versions")
    name = parts[0]
    require(bool(name) and name[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$"
            and all(ch.isascii() and (ch.isalnum() or ch in "_.$") for ch in name),
            "reject a malformed or disguised dynamic symbol")
    version: str | None = None
    default = False
    if len(parts) == 2:
        version = parts[1]
    elif len(parts) == 3:
        require(parts[1] == "", "default GNU versions require exactly two at-signs")
        version, default = parts[2], True
    if version is not None:
        require(bool(version) and len(version) <= 256
                and all(ch.isascii() and (ch.isalnum() or ch in "_.+-") for ch in version),
                "reject a missing or malformed ELF symbol version")
    return name, version, default


def parse_elf_symbols(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "the complete bounded dynamic-symbol stream is mandatory")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("the complete ELF symbol stream must be valid UTF-8") from error
    declared: int | None = None
    rows: dict[int, dict[str, Any]] = {}
    prefix, suffix = "Symbol table '.dynsym' contains ", " entries:"
    allowed_types = {"NOTYPE", "OBJECT", "FUNC", "SECTION", "FILE", "COMMON", "TLS", "GNU_IFUNC", "IFUNC"}
    allowed_binding = {"LOCAL", "GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}
    allowed_visibility = {"DEFAULT", "INTERNAL", "HIDDEN", "PROTECTED"}
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(prefix):
            require(declared is None and stripped.endswith(suffix),
                    "reject duplicated or malformed dynamic-symbol headers")
            value = stripped[len(prefix):-len(suffix)]
            require(value.isascii() and value.isdecimal() and 1 <= int(value) <= 131072,
                    "reject an invalid bounded dynamic-symbol count")
            declared = int(value)
            continue
        if stripped.startswith("Num:"):
            require(declared is not None, "the symbol table header is missing")
            continue
        columns = stripped.split()
        require(bool(columns) and columns[0].endswith(":")
                and columns[0][:-1].isascii() and columns[0][:-1].isdecimal(),
                "reject hidden or unrecognized dynamic-symbol evidence")
        require(declared is not None and 7 <= len(columns) <= 9,
                "reject omitted, shifted, or extra ELF symbol columns")
        index = int(columns[0][:-1])
        require(0 <= index < declared and index not in rows,
                "reject an out-of-range or duplicated ELF symbol row")
        address, size, kind, binding, visibility, section = columns[1:7]
        require(address.isascii() and 1 <= len(address) <= 32
                and all(ch in "0123456789abcdefABCDEF" for ch in address)
                and size.isascii() and size.isdecimal() and int(size) <= MAX_BINARY_BYTES
                and kind in allowed_types and binding in allowed_binding
                and visibility in allowed_visibility
                and (section in {"UND", "ABS", "COM"}
                     or (section.isascii() and section.isdecimal())),
                "reject malformed or shifted ELF symbol fields")
        if len(columns) == 7:
            require(index == 0 and section == "UND" and binding == "LOCAL",
                    "only the genuine null symbol may omit its name")
            rows[index] = {"index": index, "type": kind, "binding": binding,
                           "visibility": visibility, "section": section,
                           "name": None, "raw_name": None, "version": None,
                           "default_version": False, "version_index": None}
            continue
        name, version, default = checked_symbol_name(columns[7])
        version_index = None
        if len(columns) == 9:
            trailer = columns[8]
            require(version is not None and trailer.startswith("(") and trailer.endswith(")")
                    and trailer[1:-1].isascii() and trailer[1:-1].isdecimal()
                    and int(trailer[1:-1]) > 0,
                    "reject omitted or forged GNU symbol-version indexes")
            version_index = int(trailer[1:-1])
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(item) for item in FORBIDDEN_NATIVE_PREFIXES),
                "a binary delegates to a foreign matcher or process: " + name)
        rows[index] = {"index": index, "type": kind, "binding": binding,
                       "visibility": visibility, "section": section,
                       "name": name, "raw_name": columns[7], "version": version,
                       "default_version": default, "version_index": version_index}
    require(declared is not None and set(rows) == set(range(declared)),
            "reject omitted, truncated, or reordered dynamic-symbol evidence")
    ordered = [rows[index] for index in range(declared)]
    exports = {row["name"] for row in ordered
               if row["name"] is not None and row["section"] != "UND"
               and row["binding"] in {"GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}}
    undefined = {row["name"] for row in ordered
                 if row["name"] is not None and row["section"] == "UND"}
    require(bool(exports), "the genuine binary exports no owned entry point")
    return {"exports": sorted(exports), "undefined": sorted(undefined),
            "symbol_count": declared,
            "versioned_symbol_count": sum(row["version"] is not None for row in ordered),
            "symbol_records": ordered}


def matching_symbol_owner(symbol: str) -> str | None:
    if symbol.startswith("rebar_zig_"):
        return "zig"
    if symbol.startswith("rebar_go_"):
        return "go"
    if symbol.startswith("rebar_fortran_"):
        return "fortran"
    if "rebar_cpp" in symbol:
        return "cpp"
    if symbol.startswith("rebar_"):
        return "rust"
    if symbol == "PyInit__vm_native":
        return "c"
    for family in ("rust", "zig", "cpp", "go", "fortran"):
        if symbol == "PyInit__" + family + "_bridge":
            return family
    return None


def validate_elf(family: str, kind: str, dynamic: dict[str, Any], symbols: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(family)
    require(kind in FAMILIES[family]["artifacts"] and kind != "generated_header",
            "reject a substituted native artifact role")
    require(type(dynamic) is dict and type(symbols) is dict,
            "complete separately parsed dynamic and symbol evidence is mandatory")
    needed = set(dynamic.get("needed", []))
    exports, undefined = set(symbols.get("exports", [])), set(symbols.get("undefined", []))
    require(not dynamic.get("rpath"), "reject all native RPATH values")
    for symbol in exports | undefined:
        owner = matching_symbol_owner(symbol)
        require(owner is None or owner == family,
                "a native binary references another owned matching family")
    allowed = FAMILY_SYSTEM_LIBRARIES[family]
    required: frozenset[str] | set[str]
    if family == "c":
        require(kind == "extension" and "PyInit__vm_native" in exports
                and needed.issubset(allowed) and not dynamic.get("runpath"),
                "the C extension must contain its own entry point and no foreign engine")
        required = {"PyInit__vm_native"}
    elif family == "cpp":
        require(kind == "bridge" and "PyInit__cpp_bridge" in exports
                and any("rebar_cpp" in symbol for symbol in exports | undefined)
                and needed.issubset(allowed) and not dynamic.get("runpath"),
                "the C++ bridge must contain its exact owned compiled C++ engine")
        required = {"PyInit__cpp_bridge"}
    elif kind == "engine":
        required = {
            "rust": RUST_ENGINE_EXPORTS, "zig": ZIG_ENGINE_EXPORTS,
            "go": GO_ENGINE_EXPORTS, "fortran": FORTRAN_ENGINE_EXPORTS,
        }[family]
        require(set(required).issubset(exports),
                "the complete exact owned native matching exports are missing")
        if family == "fortran":
            actual_callbacks = {
                name for name in undefined if name.startswith("rebar_fortran_")
            }
            require(actual_callbacks == FORTRAN_BRIDGE_CALLBACK_EXPORTS,
                    "the Fortran engine must call exactly its three owned bridge callbacks")
        require(needed.issubset(allowed) and not dynamic.get("runpath"),
                "the matching engine resolves an external or cross-family library")
        expected_soname = FAMILIES[family]["artifacts"]["engine"]
        if family == "go":
            require(dynamic.get("soname") in ([], [expected_soname]),
                    "the Go-owned engine advertises a foreign shared-library name")
        else:
            require(dynamic.get("soname") == [expected_soname],
                    "the exact owned native engine SONAME is missing or substituted")
    else:
        engine = FAMILIES[family]["artifacts"]["engine"]
        entry = "PyInit__" + family + "_bridge"
        expected_prefix = {"rust": "rebar_", "zig": "rebar_zig_",
                           "go": "rebar_go_", "fortran": "rebar_fortran_"}[family]
        require(entry in exports and engine in needed
                and needed.issubset(allowed | {engine})
                and dynamic.get("runpath") == ["$ORIGIN"]
                and any(name.startswith(expected_prefix) for name in undefined),
                "the Python bridge must link exclusively to its adjacent owned engine")
        if family == "go":
            require(GO_ENGINE_EXPORTS.issubset(undefined),
                    "the Go bridge must call all nine exact generated-header engine exports")
        elif family == "fortran":
            require(FORTRAN_ENGINE_EXPORTS.issubset(undefined)
                    and FORTRAN_BRIDGE_CALLBACK_EXPORTS.issubset(exports),
                    "the Fortran bridge must export all three callbacks and call its nine owned engine exports")
        required = {entry}
    return {"role": kind, "needed": sorted(needed),
            "runpath": list(dynamic.get("runpath", [])),
            "soname": list(dynamic.get("soname", [])),
            "required_exports": sorted(required),
            "exports": sorted(exports), "undefined": sorted(undefined),
            "symbol_count": symbols["symbol_count"],
            "versioned_symbol_count": symbols["versioned_symbol_count"],
            "symbol_records": list(symbols["symbol_records"]),
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0}


def audit_go_generated_header(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES
            and b"Code generated by cmd/cgo; DO NOT EDIT." in raw,
            "the actual freshly generated Go c-shared header is mandatory")
    tokens = native_tokens(raw)
    names = {value for kind, value in tokens if kind == "identifier"}
    require(GO_ENGINE_EXPORTS.issubset(names),
            "the generated Go header must declare all nine exact owned ABI exports")
    require(not any(name in FORBIDDEN_NATIVE_NAMES
                    or any(name.startswith(prefix) for prefix in FORBIDDEN_NATIVE_PREFIXES)
                    for name in names),
            "the generated Go header cannot introduce an external regex engine")
    return {"generated_by": "cmd/cgo", "required_exports": sorted(GO_ENGINE_EXPORTS),
            "required_export_count": 9, "externally_supplied": False,
            "forced_bridge_include": True}


def decompress_history(raw: bytes, specification: dict[str, Any]) -> bytes:
    require(type(raw) is bytes and len(raw) == specification["archive_bytes"]
            and hashlib.sha256(raw).hexdigest() == specification["archive_sha256"],
            "the exact historical compressed archive was substituted")
    try:
        stream = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = stream.decompress(raw, MAX_REPORT_BYTES + 1)
        require(len(plain) <= MAX_REPORT_BYTES and not stream.unconsumed_tail
                and stream.eof and not stream.unused_data,
                "reject truncated, concatenated, or oversized historical archives")
        tail = stream.flush()
    except (zlib.error, ValueError) as error:
        raise BuildError("the retained historical gzip archive is invalid") from error
    plain += tail
    require(len(plain) == specification["uncompressed_bytes"]
            and hashlib.sha256(plain).hexdigest() == specification["uncompressed_sha256"],
            "the complete authentic historical report changed")
    return plain


def verify_historical_record(specification: dict[str, Any]) -> dict[str, Any]:
    family = specification["family"]
    archive_meta, archive_raw = authenticate_file(
        ROOT / checked_relative(specification["archive_path"]),
        expected=specification["archive_sha256"], maximum=MAX_ARCHIVE_BYTES,
        exact_size=specification["archive_bytes"], capture=True)
    receipt_meta, receipt_raw = authenticate_file(
        ROOT / checked_relative(specification["receipt_path"]),
        expected=specification["receipt_sha256"], maximum=MAX_SOURCE_BYTES,
        exact_size=specification["receipt_bytes"], capture=True)
    require(archive_raw is not None and receipt_raw is not None,
            "capture both complete retained historical records")
    report = decode_json(decompress_history(archive_raw, specification), canonical_required=True)
    receipt = decode_json(receipt_raw, canonical_required=True)
    require(report.get("schema") == "rebar-phase2-independent-native-source-build-v2"
            and report.get("family") == family
            and report.get("status") == specification["build_status"]
            and report.get("source_sha256") == EXPECTED_SUPPORT["build_recorder_v2"][1]
            and report.get("protocol_sha256") == EXPECTED_SUPPORT["build_protocol_v2"][1],
            "reject a relabeled or falsely passing V2 historical native report")
    processes = report.get("processes")
    require(type(processes) is list and len(processes) == specification["process_count"],
            "retain every original historical compiler and ELF process")
    seen_pids: set[int] = set()
    for process in processes:
        require(type(process) is dict and type(process.get("pid")) is int
                and process["pid"] > 0 and process["pid"] not in seen_pids
                and process.get("exit_status") == 0,
                "a genuine completed historical compiler process was omitted")
        seen_pids.add(process["pid"])
        for channel in ("stdout", "stderr"):
            encoded = process.get(channel + "_base64")
            require(type(encoded) is str, "a full historical process stream is missing")
            try:
                complete = base64.b64decode(encoded.encode("ascii"), validate=True)
            except (ValueError, UnicodeError) as error:
                raise BuildError("a historical compiler stream is malformed") from error
            require(len(complete) == process.get(channel + "_bytes")
                    and hashlib.sha256(complete).hexdigest()
                    == process.get(channel + "_sha256"),
                    "a complete historical compiler output was altered")
    require(receipt.get("schema")
            == "rebar-phase2-independent-native-source-build-v2-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == specification["build_status"]
            and receipt.get("family") == family
            and receipt.get("archive_relative") == specification["archive_path"]
            and receipt.get("archive_sha256") == specification["archive_sha256"]
            and receipt.get("archive_bytes") == specification["archive_bytes"]
            and receipt.get("uncompressed_sha256") == specification["uncompressed_sha256"]
            and receipt.get("uncompressed_bytes") == specification["uncompressed_bytes"]
            and receipt.get("source_sha256") == EXPECTED_SUPPORT["build_recorder_v2"][1]
            and receipt.get("protocol_sha256") == EXPECTED_SUPPORT["build_protocol_v2"][1],
            "the separately durable historical V2 receipt was changed or relabeled")
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases]
            == ["reference-a", "reference-b"],
            "both independently recorded historical source phases are required")
    v1 = report.get("historical_v1_c")
    require(type(v1) is dict
            and v1.get("status") == "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED",
            "the authentic falsified V1 symbol audit must remain a failure")
    if family == "zig":
        first, second = phases
        left, right = first.get("native_outputs", {}), second.get("native_outputs", {})
        require(report.get("reproducibility") is None
                and report.get("error", {}).get("type") == "BuildError"
                and left.get("engine", {}).get("size_bytes") == 480040
                and right.get("engine", {}).get("size_bytes") == 480040
                and left.get("engine", {}).get("sha256")
                == "b73d43dc4bab42abc1de92e7aaf4a0b145e242ef8407714dc1bef48fc28a7d12"
                and right.get("engine", {}).get("sha256")
                == "69a3f024c079b8994c4ffdbf37cbecf59d5afd67c8bcf5200a7331cae66d1f53"
                and left.get("bridge", {}).get("sha256")
                == "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9"
                and left.get("bridge", {}).get("sha256")
                == right.get("bridge", {}).get("sha256"),
                "the actual distinct-engine, matching-bridge Zig failure was concealed")
    else:
        reproduction = report.get("reproducibility")
        require(type(reproduction) is dict
                and reproduction.get("byte_identical") is True
                and reproduction.get("independent_fresh_phase_count") == 2,
                "a historical C/Rust passing build was not genuinely reproducible")
    return {"family": family, "build_status": specification["build_status"],
            "process_count": len(processes), "archive_sha256": archive_meta["sha256"],
            "receipt_sha256": receipt_meta["sha256"],
            "historical_v1_symbol_audit": "FALSIFIED AND PRESERVED",
            "failure_preserved": specification["build_status"] == "FAIL"}


def verify_context() -> dict[str, Any]:
    require(sys.executable == PINNED_PYTHON
            and sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314",
            "run read-only verification with the exact pinned CPython 3.14.6")
    contract_file, contract_raw = authenticate_file(
        ROOT / CONTRACT_RELATIVE, expected=None, maximum=MAX_SOURCE_BYTES, capture=True)
    require(contract_raw is not None, "the complete frozen V4 contract is required")
    contract = validate_contract(decode_json(contract_raw))
    recorder, _ = authenticate_file(ROOT / SOURCE_RELATIVE, expected=None,
                                    maximum=MAX_SOURCE_BYTES)
    protocol, _ = authenticate_file(ROOT / PROTOCOL_RELATIVE, expected=None,
                                    maximum=MAX_SOURCE_BYTES)
    support: dict[str, dict[str, Any]] = {}
    phase1: dict[str, Any] | None = None
    zig_lock: dict[str, Any] | None = None
    for key, (relative, digest, size) in EXPECTED_SUPPORT.items():
        capture = key in {"p0_manifest", "official_zig_lock", "p0_protocol"}
        record, raw = authenticate_file(ROOT / checked_relative(relative),
                                        expected=digest, maximum=MAX_SOURCE_BYTES,
                                        exact_size=size, capture=capture)
        support[key] = record
        if key == "p0_manifest":
            require(raw is not None, "the whole frozen P0 manifest is required")
            phase1 = validate_phase1_manifest(raw)
        elif key == "official_zig_lock":
            require(raw is not None, "the whole official Zig release lock is required")
            zig_lock = validate_zig_lock(raw)
    require(phase1 is not None and zig_lock is not None,
            "the immutable correctness baseline and official Zig lock are mandatory")
    owners: dict[str, dict[str, Any]] = {}
    package_closures: dict[str, dict[str, Any]] = {}
    owner_identity: set[tuple[int, int]] = set()
    for family, specification in SOURCE_OWNERS.items():
        entries: list[dict[str, Any]] = []
        captured: dict[str, bytes] = {}
        for relative, (digest, size) in specification.items():
            record, raw = authenticate_file(ROOT / checked_relative(relative),
                                            expected=digest, maximum=MAX_SOURCE_BYTES,
                                            exact_size=size, capture=True)
            require(raw is not None, "capture each exact complete owned semantic source")
            identity = (record["device"], record["inode"])
            require(identity not in owner_identity,
                    "reject cross-family hard links or reused semantic source inodes")
            owner_identity.add(identity)
            captured[relative] = raw
            if relative.endswith(".py"):
                audit = audit_python_source(raw, family=family, location=relative)
            elif relative.endswith((".c", ".cpp", ".hpp", ".rs", ".zig", ".go", ".f90")):
                audit = audit_native_source(raw, family=family, location=relative)
            else:
                audit = {"path": relative, "kind": "owned dependency-free package manifest",
                         "external_regex_dependency_count": 0,
                         "cross_family_dependency_count": 0}
            entries.append({"source": record, "audit": audit})
        if family == "rust":
            package_closures[family] = validate_cargo_closure(
                captured["candidates/rust/Cargo.toml"],
                captured["candidates/rust/Cargo.lock"])
        elif family == "go":
            package_closures[family] = validate_go_module(captured["candidates/go/go.mod"])
        owners[family] = {"language": FAMILIES[family]["language"],
                          "source_owner_count": len(entries), "sources": entries,
                          "candidate_imported": False,
                          "correctness": "NOT MEASURED"}
    tools: dict[str, dict[str, Any]] = {}
    blockers: list[dict[str, str]] = []
    for key, (path, digest, size, version, executable) in EXPECTED_TOOLCHAINS.items():
        try:
            observed, _ = authenticate_file(Path(path), expected=digest,
                                            maximum=MAX_BINARY_BYTES, exact_size=size)
            require(observed["executable"] == executable,
                    "the exact pinned compiler executable permission changed")
            tools[key] = {**observed, "pinned_version": version,
                          "version_command_run": False, "path_lookup_used": False}
        except (BuildError, OSError) as error:
            blockers.append({"toolchain": key, "path": path,
                             "error_type": type(error).__name__, "message": str(error)})
    history = [verify_historical_record(spec) for spec in EXPECTED_HISTORY.values()]
    return {
        "schema": SCHEMA + "-read-only-context", "version": 4,
        "status": "BLOCKED" if blockers else "PASS",
        "contract": contract_file, "recorder": recorder, "protocol": protocol,
        "frozen_correctness": phase1, "frozen_source_contract_schema": contract["schema"],
        "family_count": len(owners), "source_owner_count": len(owner_identity),
        "pairwise_shared_source_count": 0, "families": owners,
        "package_closures": package_closures, "official_zig_lock": zig_lock,
        "pinned_support": support, "pinned_toolchains": tools,
        "missing_or_changed_toolchains": blockers,
        "preserved_v2_history": history,
        "native_builds_started": 0, "compiler_processes_started": 0,
        "candidate_processes_started": 0, "reference_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "network_requests": 0, "hidden_cases_read": 0, "final_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "qualified_candidate_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False, "read_only": True,
    }


def command_working_directory(workdir: str, family: str, phase: str, name: str) -> Path:
    paths = phase_paths(workdir, family, phase)
    if family == "go" and name == "build_go_engine":
        return paths["go_module_directory"]
    return paths["base"]


def run_process(name: str, workdir: str, family: str, phase: str,
                steps: list[dict[str, Any]]) -> dict[str, Any]:
    require(type(steps) is list, "retain every separately identified actual process")
    expected = planned_commands(workdir, family, phase)
    require(name in expected, "an exact frozen compiler command is missing")
    argv = checked_command(name, expected[name], workdir, family, phase)
    env = build_environment(workdir, family, phase)
    cwd = command_working_directory(workdir, family, phase, name)
    empty = hashlib.sha256(b"").hexdigest()
    item: dict[str, Any] = {
        "name": name, "argv": [sanitized(value, workdir, family) for value in argv],
        "working_directory": sanitized(str(cwd), workdir, family),
        "environment": {key: sanitized(value, workdir, family)
                        for key, value in sorted(env.items())},
        "shell": False, "pid": None, "exit_status": None,
        "stdout_base64": "", "stderr_base64": "",
        "stdout_sha256": empty, "stderr_sha256": empty,
        "stdout_bytes": 0, "stderr_bytes": 0,
    }
    steps.append(item)
    try:
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=str(cwd), env=env, shell=False)
        item["pid"] = process.pid
        try:
            stdout, stderr = process.communicate(timeout=900)
        except subprocess.TimeoutExpired as error:
            process.kill()
            stdout, stderr = process.communicate()
            item["exit_status"] = process.returncode
            raise BuildError("an owned compiler exceeded its bounded runtime") from error
        item["exit_status"] = process.returncode
        require(type(stdout) is bytes and type(stderr) is bytes
                and len(stdout) <= MAX_PROCESS_BYTES and len(stderr) <= MAX_PROCESS_BYTES,
                "retain complete bounded compiler output and diagnostics")
        for channel, content in (("stdout", stdout), ("stderr", stderr)):
            item[channel + "_base64"] = base64.b64encode(content).decode("ascii")
            item[channel + "_sha256"] = hashlib.sha256(content).hexdigest()
            item[channel + "_bytes"] = len(content)
        require(process.returncode == 0,
                "the exact independently owned compiler or ELF command failed: " + name)
        return {"record": item, "stdout": stdout, "stderr": stderr}
    except (OSError, subprocess.SubprocessError) as error:
        item["error_type"] = type(error).__name__
        item["error_message"] = str(error)
        raise BuildError("an authenticated compiler process could not finish") from error


def validate_compiler_version(name: str, stdout: bytes) -> None:
    require(type(stdout) is bytes and 0 < len(stdout) <= MAX_PROCESS_BYTES,
            "capture the complete authenticated compiler version")
    first = stdout.split(b"\n", 1)[0]
    if name == "zig_version":
        require(stdout == b"0.16.0\n", "the exact official Zig 0.16.0 changed")
    elif name == "go_version":
        require(stdout == b"go version go1.26.3 linux/amd64\n",
                "the exact pinned Go 1.26.3 executable changed")
    elif name == "rustc_version":
        require(stdout.startswith(b"rustc 1.95.0 (59807616e")
                and b"release: 1.95.0\n" in stdout
                and b"commit-hash: 59807616e1fa2540724bfbac14d7976d7e4a3860\n" in stdout
                and b"host: x86_64-unknown-linux-gnu\n" in stdout,
                "the exact authenticated Rust 1.95.0 compiler changed")
    elif name == "cargo_version":
        require(stdout.startswith(b"cargo 1.95.0 (f2d3ce0bd"),
                "the exact authenticated Cargo 1.95.0 executable changed")
    elif name in {"gcc_version", "gxx_version", "gfortran_version"}:
        require(b"13." in first, "the exact GNU 13 language compiler version changed")
    elif name == "readelf_version":
        require(b"readelf" in first.lower(), "the pinned GNU ELF inspector changed")
    else:
        raise BuildError("reject an unapproved compiler-version command")


def mkdir_private(path: Path) -> None:
    require(isinstance(path, Path) and path.is_absolute(),
            "create only an exact absolute private build directory")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    result = os.lstat(str(path))
    require(stat.S_ISDIR(result.st_mode) and not stat.S_ISLNK(result.st_mode),
            "a private source-build directory was redirected")


def write_fresh(path: Path, content: bytes, *, synchronize: bool) -> dict[str, Any]:
    require(isinstance(path, Path) and path.is_absolute()
            and type(content) is bytes and 0 < len(content) <= MAX_ARCHIVE_BYTES
            and type(synchronize) is bool,
            "create only a complete bounded, explicitly owned fresh file")
    descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), 0o600)
    calls, written = 0, 0
    try:
        while written < len(content):
            amount = os.write(descriptor, content[written:])
            require(type(amount) is int and amount > 0,
                    "a fresh source or evidence write was incomplete")
            written += amount
            calls += 1
        if synchronize:
            os.fsync(descriptor)
    finally:
        os.close(descriptor)
    actual, _ = authenticate_file(path, expected=hashlib.sha256(content).hexdigest(),
                                  maximum=MAX_ARCHIVE_BYTES, exact_size=len(content))
    return {"path": actual["path"], "sha256": actual["sha256"],
            "bytes": len(content), "device": actual["device"],
            "inode": actual["inode"], "write_calls": calls,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": synchronize}


def copy_snapshot(workdir: str, family: str, phase: str,
                  sources: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    paths = phase_paths(workdir, family, phase)
    for key in ("base", "source", "native", "temporary"):
        mkdir_private(paths[key])
    additional = {
        "rust": ("cargo_home", "target"),
        "zig": ("zig_local_cache", "zig_global_cache"),
        "go": ("go_build_cache", "go_module_cache"),
        "fortran": ("fortran_modules",),
    }.get(family, ())
    for key in additional:
        mkdir_private(paths[key])
    copies: dict[str, dict[str, Any]] = {}
    for relative, raw in sorted(sources.items()):
        destination = paths["source"] / checked_relative(relative)
        mkdir_private(destination.parent)
        observed = write_fresh(destination, raw, synchronize=False)
        observed["path"] = sanitized(observed["path"], workdir, family)
        copies[relative] = observed
    return copies


def verify_fresh_artifact(workdir: str, family: str, phase: str,
                          kind: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    paths = phase_paths(workdir, family, phase)
    path = paths["artifact_" + kind]
    if kind == "generated_header":
        before, raw = authenticate_file(path, expected=None,
                                        maximum=MAX_SOURCE_BYTES, capture=True)
        require(raw is not None, "capture the complete phase-generated Go ABI header")
        audit = audit_go_generated_header(raw)
        after, _ = authenticate_file(path, expected=before["sha256"],
                                     maximum=MAX_SOURCE_BYTES,
                                     exact_size=before["size_bytes"])
    else:
        before, _ = authenticate_file(path, expected=None, maximum=MAX_BINARY_BYTES)
        dynamic = run_process(kind + "_dynamic", workdir, family, phase, steps)
        symbols = run_process(kind + "_symbols", workdir, family, phase, steps)
        audit = validate_elf(family, kind,
                             parse_elf_dynamic(dynamic["stdout"]),
                             parse_elf_symbols(symbols["stdout"]))
        after, _ = authenticate_file(path, expected=before["sha256"],
                                     maximum=MAX_BINARY_BYTES,
                                     exact_size=before["size_bytes"])
    require((before["device"], before["inode"])
            == (after["device"], after["inode"]),
            "a fresh owned binary or generated header changed during verification")
    return {"family": family, "role": kind,
            "file_name": FAMILIES[family]["artifacts"][kind],
            "path": sanitized(before["path"], workdir, family),
            "sha256": before["sha256"], "size_bytes": before["size_bytes"],
            "device": before["device"], "inode": before["inode"],
            "audit": audit, "prebuilt_artifact_read": False,
            "candidate_imported": False}


def require_fresh_absent(path: Path) -> None:
    try:
        os.lstat(str(path))
    except FileNotFoundError:
        return
    raise BuildError("reject a pre-existing, reused, or generated artifact: " + str(path))


def exact_build_phase(workdir: str, family: str, phase: str,
                      sources: dict[str, bytes], steps: list[dict[str, Any]]) -> dict[str, Any]:
    copies = copy_snapshot(workdir, family, phase, sources)
    paths = phase_paths(workdir, family, phase)
    for kind in FAMILIES[family]["artifacts"]:
        require_fresh_absent(paths["artifact_" + kind])
    version_names = [name for name in planned_commands(workdir, family, phase)
                     if name.endswith("_version")]
    for name in version_names:
        result = run_process(name, workdir, family, phase, steps)
        validate_compiler_version(name, result["stdout"])
    if family == "c":
        run_process("build_c_extension", workdir, family, phase, steps)
    elif family == "rust":
        run_process("build_rust_engine", workdir, family, phase, steps)
        engine, raw = authenticate_file(paths["rust_target_engine"], expected=None,
                                        maximum=MAX_BINARY_BYTES, capture=True)
        require(raw is not None and len(raw) == engine["size_bytes"],
                "Cargo did not produce its complete fresh owned Rust engine")
        write_fresh(paths["artifact_engine"], raw, synchronize=False)
        run_process("build_rust_bridge", workdir, family, phase, steps)
    elif family == "zig":
        run_process("build_zig_engine", workdir, family, phase, steps)
        run_process("build_zig_bridge", workdir, family, phase, steps)
    elif family == "cpp":
        run_process("build_cpp_bridge", workdir, family, phase, steps)
    elif family == "go":
        run_process("build_go_engine", workdir, family, phase, steps)
        header = verify_fresh_artifact(workdir, family, phase,
                                       "generated_header", steps)
        require(header["audit"]["forced_bridge_include"] is True,
                "the owned compiler-generated Go header must precede bridge compilation")
        run_process("build_go_bridge", workdir, family, phase, steps)
    else:
        run_process("build_fortran_engine", workdir, family, phase, steps)
        run_process("build_fortran_bridge", workdir, family, phase, steps)
    artifacts = {kind: verify_fresh_artifact(workdir, family, phase, kind, steps)
                 for kind in FAMILIES[family]["artifacts"]}
    return {"name": phase,
            "fresh_source_directory": sanitized(str(paths["source"]), workdir, family),
            "fresh_native_directory": sanitized(str(paths["native"]), workdir, family),
            "fresh_temporary_directory": sanitized(str(paths["temporary"]), workdir, family),
            "fresh_source_owners": copies,
            "native_outputs": artifacts,
            "candidate_processes_started": 0, "candidate_imports": 0,
            "native_libraries_loaded": 0, "timing_trials_run": 0,
            "hidden_cases_read": 0}


def verify_reproducible_phases(family: str, phases: Any,
                               steps: list[dict[str, Any]]) -> dict[str, Any]:
    family = checked_family(family)
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases] == ["reference-a", "reference-b"],
            "require two independent, complete, correctly ordered source-build phases")
    first, second = phases
    require(first["fresh_source_directory"] != second["fresh_source_directory"]
            and first["fresh_native_directory"] != second["fresh_native_directory"]
            and first["fresh_temporary_directory"] != second["fresh_temporary_directory"],
            "reject shared phase source, target, temporary, or output directories")
    require(set(first["fresh_source_owners"]) == set(second["fresh_source_owners"])
            == set(SOURCE_OWNERS[family]),
            "each independent source phase requires the same complete owned closure")
    for path in SOURCE_OWNERS[family]:
        left, right = first["fresh_source_owners"][path], second["fresh_source_owners"][path]
        require(left["sha256"] == right["sha256"] == SOURCE_OWNERS[family][path][0]
                and left["bytes"] == right["bytes"] == SOURCE_OWNERS[family][path][1]
                and left["path"] != right["path"]
                and (left["device"], left["inode"]) != (right["device"], right["inode"]),
                "reject reused, cross-phase, or altered source bytes and inodes")
    pids = [step.get("pid") for step in steps]
    require(all(type(pid) is int and pid > 0 for pid in pids)
            and len(pids) == len(set(pids)),
            "every compiler and ELF inspection must have its own real process")
    outputs: dict[str, Any] = {}
    for kind, filename in FAMILIES[family]["artifacts"].items():
        left, right = first["native_outputs"][kind], second["native_outputs"][kind]
        require(left["file_name"] == right["file_name"] == filename
                and left["sha256"] == right["sha256"]
                and left["size_bytes"] == right["size_bytes"]
                and left["path"] != right["path"]
                and (left["device"], left["inode"]) != (right["device"], right["inode"])
                and left["audit"] == right["audit"],
                "the two independently owned outputs are not genuinely byte-identical")
        outputs[kind] = {"file_name": filename, "sha256": left["sha256"],
                         "size_bytes": left["size_bytes"],
                         "fresh_independent_inode_count": 2,
                         "reproduced_in_two_fresh_directories": True,
                         "audit": left["audit"]}
    return {"independent_fresh_phase_count": 2, "byte_identical": True,
            "unique_process_count": len(pids), "native_outputs": outputs,
            "prebuilt_artifact_count": 0, "native_libraries_loaded": 0}


def evidence_names(family: str, label: str, *, failure: bool) -> tuple[str, str]:
    base = "native-source-build-v4-" + checked_family(family) + "-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def check_fresh_evidence(family: str, label: str) -> None:
    directory = ROOT / EVIDENCE_RELATIVE
    try:
        found = os.lstat(str(directory))
        require(stat.S_ISDIR(found.st_mode) and not stat.S_ISLNK(found.st_mode),
                "reject a redirected V4 evidence directory")
    except FileNotFoundError:
        pass
    for failed in (False, True):
        for name in evidence_names(family, label, failure=failed):
            require_fresh_absent(directory / name)


def fsync_directory(path: Path) -> dict[str, Any]:
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_DIRECTORY", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISDIR(before.st_mode), "synchronize only the owned evidence directory")
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
                "the V4 evidence directory was redirected during publication")
        return {"completed": True, "device": after.st_dev, "inode": after.st_ino}
    finally:
        os.close(descriptor)


def publish_report(report: dict[str, Any], family: str, label: str) -> dict[str, Any]:
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(family, label, failure=failed)
    directory = ROOT / EVIDENCE_RELATIVE
    mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES, "the bounded V4 source-build record is too large")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_ARCHIVE_BYTES,
            "the canonical deterministic V4 evidence archive is too large")
    actual_archive = write_fresh(directory / archive_name, archive, synchronize=True)
    archive_sync = fsync_directory(directory)
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": "PASS",
        "build_status": report["status"], "family": family, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "phase1_manifest_sha256": EXPECTED_SUPPORT["p0_manifest"][1],
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": actual_archive["sha256"],
        "archive_bytes": actual_archive["bytes"],
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "uncompressed_bytes": len(plain),
        "archive_publication": actual_archive,
        "archive_directory_fsync": archive_sync,
        "owned_source_sha256": report["owned_source_sha256"],
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False, "receipt_self_publication": "NOT CLAIMED",
    }
    raw_receipt = canonical(receipt)
    require(len(raw_receipt) <= MAX_SOURCE_BYTES, "the exact V4 durable receipt is too large")
    observed_receipt = write_fresh(directory / receipt_name, raw_receipt, synchronize=True)
    receipt_sync = fsync_directory(directory)
    return {"status": report["status"], "family": family, "label": label,
            "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
            "archive_sha256": actual_archive["sha256"],
            "receipt_relative": EVIDENCE_RELATIVE + "/" + receipt_name,
            "receipt_sha256": observed_receipt["sha256"],
            "receipt_directory_fsync": receipt_sync,
            "failure_preserved": failed, "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "holdout": "NOT OPENED"}


def authenticate_build_context(arguments: dict[str, Any]) -> dict[str, Any]:
    context = verify_context()
    require(context["status"] == "PASS" and not context["missing_or_changed_toolchains"],
            "all exact frozen owned sources and toolchains must pass before any build")
    require(context["recorder"]["sha256"] == arguments["source_sha256"]
            and context["protocol"]["sha256"] == arguments["protocol_sha256"]
            and context["contract"]["sha256"] == arguments["contract_sha256"],
            "the caller must independently pin the published V4 source, protocol, and contract")
    checked_source_pins(arguments["family"], arguments["owned_source_sha256"])
    return context


def run_build(arguments: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    family, label = checked_family(arguments["family"]), checked_label(arguments["label"])
    check_fresh_evidence(family, label)
    context = authenticate_build_context(arguments)
    pins = checked_source_pins(family, arguments["owned_source_sha256"])
    report: dict[str, Any] = {
        "schema": SCHEMA, "version": 4, "status": "FAIL",
        "family": family, "label": label,
        "source_sha256": arguments["source_sha256"],
        "protocol_sha256": arguments["protocol_sha256"],
        "contract_sha256": arguments["contract_sha256"],
        "owned_source_sha256": pins,
        "frozen_correctness": context["frozen_correctness"],
        "preserved_v2_history": context["preserved_v2_history"],
        "pinned_toolchains": context["pinned_toolchains"],
        "processes": [], "build_phases": [], "reproducibility": None,
        "candidate_processes_started": 0, "reference_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "network_requests": 0, "hidden_cases_read": 0,
        "final_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    sources: dict[str, bytes] = {}
    before: dict[str, dict[str, Any]] = {}
    for relative, digest in pins.items():
        size = SOURCE_OWNERS[family][relative][1]
        observed, raw = authenticate_file(ROOT / relative, expected=digest,
                                          maximum=MAX_SOURCE_BYTES,
                                          exact_size=size, capture=True)
        require(raw is not None, "capture the whole independently owned source before building")
        before[relative], sources[relative] = observed, raw
    report["owned_source_before"] = before
    root = tempfile.mkdtemp(prefix=WORK_PREFIX + family + "-", dir="/tmp")
    checked_workdir(root, family)
    actual_root = os.lstat(root)
    require(stat.S_ISDIR(actual_root.st_mode)
            and stat.S_IMODE(actual_root.st_mode) == 0o700,
            "the actual fresh source root must have private mode 0700")
    report["fresh_private_root"] = sanitized(root, root, family)
    try:
        for phase in ("reference-a", "reference-b"):
            report["build_phases"].append(exact_build_phase(
                root, family, phase, sources, report["processes"]))
        report["reproducibility"] = verify_reproducible_phases(
            family, report["build_phases"], report["processes"])
        after = authenticate_build_context(arguments)
        require(after["contract"]["sha256"] == context["contract"]["sha256"]
                and after["recorder"]["sha256"] == context["recorder"]["sha256"]
                and after["protocol"]["sha256"] == context["protocol"]["sha256"],
                "the exact frozen V4 source context changed during the two builds")
        latest: dict[str, dict[str, Any]] = {}
        for relative, digest in pins.items():
            observed, _ = authenticate_file(ROOT / relative, expected=digest,
                                            maximum=MAX_SOURCE_BYTES,
                                            exact_size=SOURCE_OWNERS[family][relative][1])
            require((observed["device"], observed["inode"], observed["sha256"])
                    == (before[relative]["device"], before[relative]["inode"],
                        before[relative]["sha256"]),
                    "an owned source inode or complete bytes changed during the builds")
            latest[relative] = observed
        report["owned_source_after"] = latest
        report["status"] = "PASS"
    except (BuildError, OSError, ValueError, UnicodeError,
            subprocess.SubprocessError) as error:
        report["status"] = "FAIL"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    published = publish_report(report, family, label)
    return (0 if report["status"] == "PASS" else 1), published


class SyntheticSandbox:
    """Reject and count every external effect during in-memory controls."""

    def __init__(self) -> None:
        self.original: list[tuple[Any, str, Any]] = []
        self.counts = {
            "actual_file_reads": 0, "actual_file_writes": 0,
            "actual_processes": 0, "actual_threads": 0,
            "actual_clocks": 0, "actual_network": 0,
            "actual_candidate_imports": 0,
            "actual_native_library_loads": 0,
            "actual_holdout_reads": 0,
            "blocked_file_operations": 0,
            "blocked_process_operations": 0,
            "blocked_thread_operations": 0,
            "blocked_clock_operations": 0,
            "blocked_network_operations": 0,
            "blocked_import_operations": 0,
            "blocked_temporary_operations": 0,
            "blocked_native_library_loads": 0,
        }

    def install(self, owner: Any, name: str, replacement: Any) -> None:
        self.original.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)

    def deny(self, key: str, description: str) -> Any:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            self.counts[key] += 1
            raise SourceOnlyError(description)
        return blocked

    def __enter__(self) -> SyntheticSandbox:
        files = self.deny("blocked_file_operations",
                          "in-memory source controls cannot read or write files")
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "write"), (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "listdir"), (os, "scandir"), (os, "mkdir"),
            (os, "makedirs"), (os, "unlink"), (os, "remove"),
            (os, "replace"), (os, "rename"), (os, "link"), (os, "fsync"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "stat"),
            (Path, "lstat"), (Path, "exists"), (Path, "is_file"),
            (Path, "is_dir"), (Path, "mkdir"), (Path, "iterdir"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, files)
        processes = self.deny("blocked_process_operations",
                              "source controls cannot start a compiler or subprocess")
        for owner, name in (
            (subprocess, "Popen"), (subprocess, "run"),
            (subprocess, "check_call"), (subprocess, "check_output"),
            (os, "system"), (os, "popen"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, processes)
        for name in ("mkdtemp", "mkstemp", "TemporaryDirectory"):
            if hasattr(tempfile, name):
                self.install(tempfile, name, self.deny(
                    "blocked_temporary_operations",
                    "source controls cannot create a build directory"))
        self.install(threading.Thread, "start", self.deny(
            "blocked_thread_operations", "source controls cannot start a thread"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time", "thread_time"):
            if hasattr(time, name):
                self.install(time, name, self.deny(
                    "blocked_clock_operations", "source controls cannot measure a clock"))
        self.install(socket, "socket", self.deny(
            "blocked_network_operations", "source controls cannot open a network"))
        self.install(importlib, "import_module", self.deny(
            "blocked_import_operations", "source controls cannot import a candidate"))
        self.install(ctypes, "CDLL", self.deny(
            "blocked_native_library_loads", "source controls cannot load a native engine"))
        return self

    def __exit__(self, kind: Any, value: Any, trace: Any) -> bool:
        for owner, name, original in reversed(self.original):
            setattr(owner, name, original)
        return False


def synthetic_dynamic(*, needed: tuple[str, ...] = (),
                      soname: str | None = None,
                      runpath: str | None = None,
                      rpath: str | None = None) -> bytes:
    rows = ["Dynamic section at offset 0x1 contains 1 entry:"]
    for name in needed:
        rows.append(" 0x1 (NEEDED) Shared library: [" + name + "]")
    for marker, value in (("SONAME", soname), ("RUNPATH", runpath), ("RPATH", rpath)):
        if value is not None:
            rows.append(" 0x1 (" + marker + ") Value: [" + value + "]")
    return ("\n".join(rows) + "\n").encode("ascii")


def synthetic_symbols(exports: tuple[str, ...], undefined: tuple[str, ...] = ()) -> bytes:
    require(type(exports) is tuple and type(undefined) is tuple,
            "synthetic symbols require separately identified tuples")
    total = 1 + len(exports) + len(undefined)
    rows = ["Symbol table '.dynsym' contains " + str(total) + " entries:",
            "   Num: Value Size Type Bind Vis Ndx Name",
            "     0: 0000000000000000 0 NOTYPE LOCAL DEFAULT UND"]
    index = 1
    for section, names in (("12", exports), ("UND", undefined)):
        for name in names:
            rows.append(str(index) + ": 0000000000000000 1 FUNC GLOBAL DEFAULT "
                        + section + " " + name
                        + (" (2)" if "@" in name else ""))
            index += 1
    return ("\n".join(rows) + "\n").encode("ascii")


def parse_arguments(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list and all(type(value) is str for value in arguments),
            "supply only exact frozen source-build command arguments")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    if arguments == ["--verify-context"]:
        return {"mode": "verify-context"}
    require(bool(arguments) and arguments[0] == "--build",
            "select only --self-test, --verify-context, or an explicitly pinned --build")
    result: dict[str, Any] = {"mode": "build", "owned_source_sha256": []}
    options = {"--family": "family", "--label": "label",
               "--source-sha256": "source_sha256",
               "--protocol-sha256": "protocol_sha256",
               "--contract-sha256": "contract_sha256"}
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments), "a frozen build option lacks its exact value")
        option, value = arguments[position], arguments[position + 1]
        if option == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(option in options and options[option] not in result,
                    "reject repeated, hidden, abbreviated, or benchmark build options")
            result[options[option]] = value
        position += 2
    require(set(result) == {"mode", "family", "label", "source_sha256",
                            "protocol_sha256", "contract_sha256", "owned_source_sha256"},
            "pin the V4 recorder, protocol, contract, family, label, and every owned source")
    checked_family(result["family"])
    checked_label(result["label"])
    for key in ("source_sha256", "protocol_sha256", "contract_sha256"):
        checked_digest(result[key], key)
    checked_source_pins(result["family"], result["owned_source_sha256"])
    return result


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, result: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "each synthetic positive control needs a distinct identity")
        require(bool(result), "a required V4 source control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "each hostile synthetic control needs a distinct identity")
        try:
            operation()
        except (BuildError, OSError, TypeError, ValueError, UnicodeError,
                RecursionError, OverflowError):
            rejected.append(name)
            return
        raise BuildError("an unsafe V4 source-freeze attack was accepted: " + name)

    with SyntheticSandbox() as guard:
        contract = expected_contract()
        accept("exact-six-family-twenty-five-owner-contract",
               validate_contract(contract)["family_count"] == 6
               and sum(len(item["owners"]) for item in contract["families"]) == 25)
        accept("no-qualified-candidates-and-exact-31237-reference-cases",
               contract["qualified_candidate_count"] == 0
               and contract["oracle"] == expected_oracle())
        accept("complete-pairwise-disjoint-owned-source-closures",
               len({path for graph in SOURCE_OWNERS.values() for path in graph}) == 25)
        accept("absolute-real-go-compiler-not-symlink-or-path-lookup",
               PINNED_GO == "/home/dev-user/.openai/go/bin/go"
               and EXPECTED_TOOLCHAINS["go"][1]
               == "d68b7abbc40d0844f673f6cf06ae3cded225c50437c6454fa37ef178d079fe65")
        accept("official-zig-compiler-independent-of-ambient-path",
               PINNED_ZIG == "/tmp/zig-x86_64-linux-0.16.0/zig"
               and EXPECTED_TOOLCHAINS["zig"][4] is True)
        accept("preserve-cpp-header-and-all-nine-rust-owners",
               "candidates/cpp/engine.hpp" in SOURCE_OWNERS["cpp"]
               and len(SOURCE_OWNERS["rust"]) == 9)
        accept("preserve-actual-failed-zig-history",
               EXPECTED_HISTORY["zig"]["build_status"] == "FAIL"
               and EXPECTED_HISTORY["zig"]["process_count"] == 15)
        accept("exact-nine-go-generated-abi-exports", len(GO_ENGINE_EXPORTS) == 9)
        accept("exact-three-owned-fortran-bridge-callback-exports",
               len(FORTRAN_BRIDGE_CALLBACK_EXPORTS) == 3
               and len(FORTRAN_ENGINE_EXPORTS) == 9)
        accept("family-specific-cpp-runtime-only",
               "libstdc++.so.6" in FAMILY_SYSTEM_LIBRARIES["cpp"]
               and all("libstdc++.so.6" not in FAMILY_SYSTEM_LIBRARIES[name]
                       for name in FAMILIES if name != "cpp"))
        accept("family-specific-fortran-runtime-only",
               "libgfortran.so.5" in FAMILY_SYSTEM_LIBRARIES["fortran"]
               and all("libgfortran.so.5" not in FAMILY_SYSTEM_LIBRARIES[name]
                       for name in FAMILIES if name != "fortran"))
        accept("unicode-support-imports-not-regex-delegation",
               FAMILIES["cpp"]["allowed_bridge_python_imports"] == ("unicodedata",)
               and FAMILIES["go"]["allowed_bridge_python_imports"] == ("unicodedata",))
        accept("separate-read-only-context-command",
               parse_arguments(["--verify-context"]) == {"mode": "verify-context"})
        accept("separate-in-memory-self-test-command",
               parse_arguments(["--self-test"]) == {"mode": "self-test"})
        accept("stable-large-integer-and-lone-surrogate-canonical-json",
               decode_json(canonical({"n": 6001118316486346290,
                                      "maximum": 18446744073709551615,
                                      "surrogate": "\ud800"}), canonical_required=True)
               == {"n": 6001118316486346290,
                   "maximum": 18446744073709551615, "surrogate": "\ud800"})
        accept("deterministic-single-member-zero-mtime-gzip",
               gzip.compress(canonical({"v": 4}), compresslevel=9, mtime=0)
               == gzip.compress(canonical({"v": 4}), compresslevel=9, mtime=0))
        for name in FAMILIES:
            pins = [path + "=" + digest
                    for path, (digest, _) in SOURCE_OWNERS[name].items()]
            accept(name + "-exact-owned-source-pins",
                   set(checked_source_pins(name, pins)) == set(SOURCE_OWNERS[name]))
            root = "/tmp/" + WORK_PREFIX + name + "-synthetic"
            first, second = phase_paths(root, name, "reference-a"), phase_paths(root, name, "reference-b")
            accept(name + "-distinct-source-output-temporary-and-cache-plans",
                   first["source"] != second["source"]
                   and first["native"] != second["native"]
                   and first["temporary"] != second["temporary"]
                   and first["target"] != second["target"]
                   and first["zig_local_cache"] != second["zig_local_cache"]
                   and first["zig_global_cache"] != second["zig_global_cache"]
                   and first["go_build_cache"] != second["go_build_cache"]
                   and first["go_module_cache"] != second["go_module_cache"])
            commands = planned_commands(root, name, "reference-a")
            accept(name + "-direct-pinned-compiler-and-inspector-argv",
                   all(checked_command(key, argv, root, name, "reference-a") == argv
                       for key, argv in commands.items()))
            reject(name + "-reject-missing-owned-source",
                   lambda name=name, pins=pins: checked_source_pins(name, pins[:-1]))
            reject(name + "-reject-duplicate-owned-source",
                   lambda name=name, pins=pins: checked_source_pins(
                       name, pins[:-1] + [pins[0]]))
            sibling = next(key for key in FAMILIES if key != name)
            foreign = next(iter(SOURCE_OWNERS[sibling].items()))
            foreign_pin = foreign[0] + "=" + foreign[1][0]
            reject(name + "-reject-cross-family-semantic-source",
                   lambda name=name, pins=pins, item=foreign_pin:
                   checked_source_pins(name, pins[:-1] + [item]))
            modified = pins.copy()
            modified[0] = modified[0].split("=", 1)[0] + "=" + "0" * 64
            reject(name + "-reject-stale-owner-digest",
                   lambda name=name, modified=modified:
                   checked_source_pins(name, modified))
            for bad in ("/tmp/foreign", "/", "/tmp", "/tmp/" + WORK_PREFIX + "other-x",
                        "/tmp/" + WORK_PREFIX + name + "-x/../outside"):
                reject(name + "-reject-private-root-" + str(len(rejected)),
                       lambda bad=bad, name=name: checked_workdir(bad, name))
            first_name, first_argv = next(iter(commands.items()))
            reject(name + "-reject-foreign-compiler",
                   lambda first_name=first_name, first_argv=first_argv,
                   root=root, name=name: checked_command(
                       first_name, ["/usr/bin/false", *first_argv[1:]],
                       root, name, "reference-a"))
        go_root = "/tmp/" + WORK_PREFIX + "go-synthetic"
        go_commands = planned_commands(go_root, "go", "reference-a")
        go_env = build_environment(go_root, "go", "reference-a")
        go_paths = phase_paths(go_root, "go", "reference-a")
        accept("go-offline-no-registry-no-ambient-toolchain",
               go_env["GOPROXY"] == "off" and go_env["GOSUMDB"] == "off"
               and go_env["GOWORK"] == "off" and go_env["GOENV"] == "off"
               and go_env["GOTOOLCHAIN"] == "local"
               and go_env["CC"] == PINNED_GCC)
        accept("go-c-shared-command-owns-generated-header",
               "-buildmode=c-shared" in go_commands["build_go_engine"]
               and "-include" in go_commands["build_go_bridge"]
               and str(go_paths["artifact_generated_header"])
               in go_commands["build_go_bridge"]
               and command_working_directory(go_root, "go", "reference-a", "build_go_engine")
               == go_paths["go_module_directory"])
        synthetic_header = (b"/* Code generated by cmd/cgo; DO NOT EDIT. */\n"
                            + b"\n".join(("extern void " + name + "(void);").encode("ascii")
                                         for name in sorted(GO_ENGINE_EXPORTS)) + b"\n")
        accept("go-authenticated-generated-header-declares-nine-exports",
               audit_go_generated_header(synthetic_header)["required_export_count"] == 9)
        for name in sorted(GO_ENGINE_EXPORTS):
            reject("go-reject-generated-header-missing-" + name,
                   lambda name=name: audit_go_generated_header(
                       synthetic_header.replace(("extern void " + name + "(void);\n")
                                                .encode("ascii"), b"")))
        reject("go-reject-foreign-handwritten-generated-header",
               lambda: audit_go_generated_header(
                   synthetic_header.replace(b"Code generated by cmd/cgo; DO NOT EDIT.",
                                            b"A handwritten external header")))
        reject("go-reject-hidden-stdlib-regexp-import",
               lambda: audit_native_source(
                   b'package main\nimport "regexp"\nfunc rebar_go_compile() {}\n',
                   family="go", location="candidates/go/engine.go"))
        reject("go-reject-hidden-stdlib-regexp-syntax-import",
               lambda: audit_native_source(
                   b'package main\nimport ("regexp/syntax")\nfunc rebar_go_compile() {}\n',
                   family="go", location="candidates/go/engine.go"))
        reject("go-reject-third-party-import",
               lambda: audit_native_source(
                   b'package main\nimport "github.com/vendor/engine"\n',
                   family="go", location="candidates/go/engine.go"))
        reject("go-reject-dependent-go-module",
               lambda: validate_go_module(
                   b"module rebar.local/candidates/go\n\ngo 1.26.0\nrequire example.com/regex v1.0.0\n"))
        reject("cpp-reject-cpp-stdlib-regex-header",
               lambda: audit_native_source(b"#include <regex>\nnamespace rebar_cpp {}\n",
                                           family="cpp", location="candidates/cpp/engine.hpp"))
        reject("cpp-reject-std-regex-delegation",
               lambda: audit_native_source(b"namespace rebar_cpp { std::regex matcher; }\n",
                                           family="cpp", location="candidates/cpp/engine.cpp"))
        reject("cpp-reject-boost-regex-delegation",
               lambda: audit_native_source(b"#include <boost/regex.hpp>\nnamespace rebar_cpp {}\n",
                                           family="cpp", location="candidates/cpp/engine.hpp"))
        reject("fortran-reject-case-insensitive-process-delegation",
               lambda: audit_native_source(
                   b"module x\ncontains\nsubroutine rebar_fortran_compile()\n"
                   b"call EXECUTE_COMMAND_LINE('foreign')\nend subroutine\nend module\n",
                   family="fortran", location="candidates/fortran/engine.f90"))
        accept("fortran-comments-do-not-create-false-delegation",
               audit_native_source(
                   b"! execute_command_line regex\n"
                   b"module x\ncontains\nsubroutine rebar_fortran_compile()\n"
                   b"end subroutine\nend module\n",
                   family="fortran", location="candidates/fortran/engine.f90")
               ["external_regex_dependency_count"] == 0)
        zig_root = "/tmp/" + WORK_PREFIX + "zig-synthetic"
        zig_command = planned_commands(zig_root, "zig", "reference-a")["build_zig_engine"]
        accept("zig-preserves-official-native-strip-correction",
               zig_command.count("-fstrip") == 1
               and "-fno-strip" not in zig_command
               and "--cache-dir" in zig_command
               and "--global-cache-dir" in zig_command)
        reject("zig-reject-missing-native-strip-flag",
               lambda: checked_command("build_zig_engine",
                                       [value for value in zig_command if value != "-fstrip"],
                                       zig_root, "zig", "reference-a"))
        reject("zig-reject-duplicate-native-strip-flag",
               lambda: checked_command("build_zig_engine", [*zig_command, "-fstrip"],
                                       zig_root, "zig", "reference-a"))
        reject("go-reject-omitted-forced-generated-header",
               lambda: checked_command(
                   "build_go_bridge",
                   [value for value in go_commands["build_go_bridge"]
                    if value not in {"-include", str(go_paths["artifact_generated_header"])}],
                   go_root, "go", "reference-a"))
        accept("exact-local-origin-runpath-parser",
               parse_elf_dynamic(synthetic_dynamic(
                   needed=("_go_engine.so", "libc.so.6"), runpath="$ORIGIN"))
               ["runpath"] == ["$ORIGIN"])
        for family, entry in (("c", "PyInit__vm_native"),
                              ("cpp", "PyInit__cpp_bridge")):
            exports = (entry,) if family == "c" else (entry, "rebar_cpp_owned")
            parsed = parse_elf_symbols(synthetic_symbols(exports))
            audit = validate_elf(family, "extension" if family == "c" else "bridge",
                                 parse_elf_dynamic(synthetic_dynamic(needed=("libc.so.6",))),
                                 parsed)
            accept(family + "-exact-owned-synthetic-elf", audit["required_exports"] == [entry])
        for family, required in (("rust", RUST_ENGINE_EXPORTS),
                                 ("zig", ZIG_ENGINE_EXPORTS),
                                 ("go", GO_ENGINE_EXPORTS),
                                 ("fortran", FORTRAN_ENGINE_EXPORTS)):
            engine_name = FAMILIES[family]["artifacts"]["engine"]
            dynamic = parse_elf_dynamic(synthetic_dynamic(
                needed=("libc.so.6",), soname=engine_name))
            engine_callbacks = (tuple(sorted(FORTRAN_BRIDGE_CALLBACK_EXPORTS))
                                if family == "fortran" else ())
            symbols = parse_elf_symbols(synthetic_symbols(
                tuple(sorted(required)), engine_callbacks))
            accept(family + "-complete-owned-engine-elf",
                   set(validate_elf(family, "engine", dynamic, symbols)
                       ["required_exports"]) == required)
            entry = "PyInit__" + family + "_bridge"
            own_symbol = next(iter(sorted(required)))
            bridge_dynamic = parse_elf_dynamic(synthetic_dynamic(
                needed=(engine_name, "libc.so.6"), runpath="$ORIGIN"))
            bridge_exports = ((entry, *tuple(sorted(FORTRAN_BRIDGE_CALLBACK_EXPORTS)))
                              if family == "fortran" else (entry,))
            bridge_undefined = (tuple(sorted(required))
                                if family in {"go", "fortran"} else (own_symbol,))
            bridge_symbols = parse_elf_symbols(synthetic_symbols(
                bridge_exports, bridge_undefined))
            accept(family + "-owned-adjacent-origin-bridge-elf",
                   validate_elf(family, "bridge", bridge_dynamic, bridge_symbols)
                   ["runpath"] == ["$ORIGIN"])
            reject(family + "-reject-unsafe-rpath",
                   lambda family=family, symbols=symbols, engine_name=engine_name:
                   validate_elf(family, "engine", parse_elf_dynamic(synthetic_dynamic(
                       needed=("libc.so.6",), soname=engine_name, rpath="/tmp/foreign")),
                       symbols))
            reject(family + "-reject-foreign-regex-library",
                   lambda family=family, symbols=symbols, engine_name=engine_name:
                   validate_elf(family, "engine", parse_elf_dynamic(synthetic_dynamic(
                       needed=("libpcre2-8.so.0",), soname=engine_name)), symbols))
            reject(family + "-reject-non-origin-bridge-runpath",
                   lambda family=family, bridge_symbols=bridge_symbols,
                   engine_name=engine_name: validate_elf(
                       family, "bridge", parse_elf_dynamic(synthetic_dynamic(
                           needed=(engine_name, "libc.so.6"), runpath="/tmp/foreign")),
                       bridge_symbols))
            if family == "fortran":
                for callback in sorted(FORTRAN_BRIDGE_CALLBACK_EXPORTS):
                    omitted_callbacks = tuple(
                        name for name in sorted(FORTRAN_BRIDGE_CALLBACK_EXPORTS)
                        if name != callback)
                    reject("fortran-reject-missing-engine-callback-" + callback,
                           lambda omitted_callbacks=omitted_callbacks,
                           required=required, dynamic=dynamic: validate_elf(
                               "fortran", "engine", dynamic,
                               parse_elf_symbols(synthetic_symbols(
                                   tuple(sorted(required)), omitted_callbacks))))
                    reject("fortran-reject-missing-bridge-callback-" + callback,
                           lambda callback=callback, bridge_dynamic=bridge_dynamic,
                           bridge_undefined=bridge_undefined: validate_elf(
                               "fortran", "bridge", bridge_dynamic,
                               parse_elf_symbols(synthetic_symbols(
                                   ("PyInit__fortran_bridge", *tuple(
                                       name for name in sorted(FORTRAN_BRIDGE_CALLBACK_EXPORTS)
                                       if name != callback)), bridge_undefined))))
        versioned = parse_elf_symbols(synthetic_symbols(
            ("PyInit__vm_native",), ("malloc@GLIBC_2.2.5",)))
        accept("preserve-authentic-versioned-undefined-elf-symbol",
               versioned["versioned_symbol_count"] == 1
               and "malloc" in versioned["undefined"])
        reject("reject-hidden-or-truncated-versioned-symbol-table",
               lambda: parse_elf_symbols(
                   synthetic_symbols(("PyInit__vm_native",))[:-1]))
        reject("reject-concealed-external-native-regex-symbol",
               lambda: parse_elf_symbols(
                   synthetic_symbols(("PyInit__vm_native",), ("pcre2_match",))))
        for bad in ("../escape", "/absolute/path", "a//b", "a/./b",
                    "a/../b", "a\\b", "a\x00b"):
            reject("reject-source-traversal-" + str(len(rejected)),
                   lambda bad=bad: checked_relative(bad))
        reject("reject-duplicate-json-keys",
               lambda: decode_json(b'{"owner":1,"owner":2}\n'))
        reject("reject-nonfinite-json-nan",
               lambda: decode_json(b'{"owner":NaN}\n'))
        reject("reject-nonfinite-json-infinity",
               lambda: decode_json(b'{"owner":Infinity}\n'))
        reject("reject-noncanonical-signed-json",
               lambda: decode_json(b'{ "owner": 1 }\n', canonical_required=True))
        reject("reject-short-digest", lambda: checked_digest("0" * 63, "synthetic"))
        reject("reject-uppercase-digest", lambda: checked_digest("A" * 64, "synthetic"))
        for field, poisoned in (
            ("schema", "rebar-phase2-independent-native-source-build-v3-source-freeze"),
            ("version", 3), ("family_count", 5),
            ("qualified_candidate_count", 1),
            ("phase", "BUILD AUTHORIZED"),
        ):
            hostile = copy.deepcopy(contract)
            hostile[field] = poisoned
            reject("reject-substituted-contract-" + field,
                   lambda hostile=hostile: validate_contract(hostile))
        missing_header = copy.deepcopy(contract)
        cpp = next(item for item in missing_header["families"] if item["id"] == "cpp")
        cpp["owners"] = [item for item in cpp["owners"]
                         if item["path"] != "candidates/cpp/engine.hpp"]
        reject("reject-omitted-frozen-cpp-semantic-header",
               lambda: validate_contract(missing_header))
        hidden_holdout = copy.deepcopy(contract)
        hidden_holdout["phase_boundary"]["hidden_cases_read"] = 1
        reject("reject-opened-hidden-holdout", lambda: validate_contract(hidden_holdout))
        false_zig = copy.deepcopy(contract)
        next(item for item in false_zig["historical_v2"]
             if item["family"] == "zig")["build_status"] = "PASS"
        reject("reject-reclassified-authentic-zig-failure",
               lambda: validate_contract(false_zig))
        support_import = b'#include <Python.h>\nvoid f(void) { PyImport_ImportModule("unicodedata"); }\n'
        for family, location in (("cpp", "candidates/cpp/py_bridge.cpp"),
                                 ("go", "candidates/go/py_bridge.c")):
            required_entry = ("PyMODINIT_FUNC PyInit__" + family + "_bridge(void) {}\n").encode("ascii")
            accept(family + "-allows-only-owned-literal-unicode-support",
                   audit_native_source(support_import + required_entry,
                                       family=family, location=location)
                   ["native_literal_imports"] == ["unicodedata"])
            reject(family + "-rejects-python-stdlib-re-support-import",
                   lambda family=family, location=location, required_entry=required_entry:
                   audit_native_source(
                       support_import.replace(b'"unicodedata"', b'"re"') + required_entry,
                       family=family, location=location))
        reject("reject-unpinned-hidden-cli-option",
               lambda: parse_arguments(["--verify-context", "--benchmark"]))
        reject("reject-unpinned-build-without-source-closure",
               lambda: parse_arguments(["--build", "--family", "go"]))
        for name, operation in (
            ("file-read", lambda: builtins.open("/forbidden", "rb")),
            ("file-stat", lambda: os.stat("/forbidden")),
            ("candidate-process", lambda: subprocess.run(["/usr/bin/false"])),
            ("temporary-directory", lambda: tempfile.mkdtemp()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.socket()),
            ("candidate-import", lambda: importlib.import_module("candidates.go_candidate")),
            ("native-library", lambda: ctypes.CDLL("/foreign.so")),
        ):
            reject("effect-wall-blocks-" + name, operation)
        actual_effects = (
            "actual_file_reads", "actual_file_writes", "actual_processes",
            "actual_threads", "actual_clocks", "actual_network",
            "actual_candidate_imports", "actual_native_library_loads",
            "actual_holdout_reads",
        )
        require(all(guard.counts[key] == 0 for key in actual_effects),
                "source-only controls performed a real external action")
        require(all(guard.counts[key] > 0 for key in (
            "blocked_file_operations", "blocked_process_operations",
            "blocked_thread_operations", "blocked_clock_operations",
            "blocked_network_operations", "blocked_import_operations",
            "blocked_temporary_operations", "blocked_native_library_loads",
        )), "every real-effect guard must itself be exercised")
        counters = dict(guard.counts)
    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "version": 4, "status": "PASS", "synthetic": True,
        "positive_control_count": len(accepted), "positive_controls": accepted,
        "rejected_attack_count": len(rejected), "rejected_attacks": rejected,
        "guard_counters": counters, "family_count": 6,
        "source_owner_count": 25, "qualified_candidate_count": 0,
        "candidate_workers_started": 0, "reference_workers_started": 0,
        "compiler_processes_started": 0, "native_builds_started": 0,
        "native_libraries_loaded": 0, "network_requests": 0,
        "hidden_cases_read": 0, "final_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "winner_selected": False,
        "holdout": "NOT OPENED",
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if selected["mode"] == "self-test":
            result, exit_code = self_test(), 0
        elif selected["mode"] == "verify-context":
            result = verify_context()
            exit_code = 0 if result["status"] == "PASS" else 1
        else:
            exit_code, result = run_build(selected)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return exit_code
    except (BuildError, OSError, ValueError, UnicodeError, zlib.error,
            tomllib.TOMLDecodeError) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
