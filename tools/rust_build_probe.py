#!/usr/bin/env python3
"""Compare isolated Rust release builds against frozen, real Python workloads.

Every variant has its own temporary Rust engine and CPython extension. The
installed candidate, the held-out cases, and the frozen benchmark are never
modified. Only practice cases are used for build selection.
"""

from __future__ import annotations

import argparse
import base64
import gc
import gzip
import hashlib
import importlib
import io
import json
import math
import os
import platform
import random
import shutil
import statistics
import struct
import subprocess
import sys
import sysconfig
import tempfile
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORDER_SEED = 1985072301
BOOTSTRAP_SEED = 1985072302
REGRESSION_SLOWDOWN_RATIO = 1.2


@dataclass(frozen=True)
class Variant:
    name: str
    rustflags: tuple[str, ...] = ()
    profile: tuple[tuple[str, str], ...] = ()
    compiler: str = "cc"
    bridge_flags: tuple[str, ...] = ()
    static_bridge: bool = False
    portable: bool = True


VARIANTS = (
    Variant("baseline"),
    Variant("rust-thin-lto", profile=(("LTO", "thin"),)),
    Variant("rust-no-lto", profile=(("LTO", "false"),)),
    Variant("rust-opt-2", profile=(("OPT_LEVEL", "2"),)),
    Variant("rust-opt-s", profile=(("OPT_LEVEL", "s"),)),
    Variant("rust-opt-z", profile=(("OPT_LEVEL", "z"),)),
    Variant("rust-cgu-4", profile=(("CODEGEN_UNITS", "4"),)),
    Variant("rust-cgu-8", profile=(("CODEGEN_UNITS", "8"),)),
    Variant("rust-cgu-16", profile=(("CODEGEN_UNITS", "16"),)),
    Variant(
        "rust-thin-cgu-4",
        profile=(("CODEGEN_UNITS", "4"), ("LTO", "thin")),
    ),
    Variant(
        "rust-thin-cgu-8",
        profile=(("CODEGEN_UNITS", "8"), ("LTO", "thin")),
    ),
    Variant(
        "rust-thin-cgu-16",
        profile=(("CODEGEN_UNITS", "16"), ("LTO", "thin")),
    ),
    Variant("rust-inline-25", rustflags=("-Cllvm-args=--inline-threshold=25",)),
    Variant("rust-inline-75", rustflags=("-Cllvm-args=--inline-threshold=75",)),
    Variant("rust-inline-100", rustflags=("-Cllvm-args=--inline-threshold=100",)),
    Variant("rust-inline-150", rustflags=("-Cllvm-args=--inline-threshold=150",)),
    Variant("rust-inline-225", rustflags=("-Cllvm-args=--inline-threshold=225",)),
    Variant("rust-inline-300", rustflags=("-Cllvm-args=--inline-threshold=300",)),
    Variant("rust-inline-350", rustflags=("-Cllvm-args=--inline-threshold=350",)),
    Variant("rust-inline-450", rustflags=("-Cllvm-args=--inline-threshold=450",)),
    Variant("rust-inline-550", rustflags=("-Cllvm-args=--inline-threshold=550",)),
    Variant("rust-inline-700", rustflags=("-Cllvm-args=--inline-threshold=700",)),
    Variant("rust-inline-1000", rustflags=("-Cllvm-args=--inline-threshold=1000",)),
    Variant("rust-unroll-64", rustflags=("-Cllvm-args=--unroll-threshold=64",)),
    Variant("rust-unroll-128", rustflags=("-Cllvm-args=--unroll-threshold=128",)),
    Variant("rust-unroll-256", rustflags=("-Cllvm-args=--unroll-threshold=256",)),
    Variant("rust-unroll-512", rustflags=("-Cllvm-args=--unroll-threshold=512",)),
    Variant("rust-unroll-1024", rustflags=("-Cllvm-args=--unroll-threshold=1024",)),
    Variant("rust-no-loop-vectorize", rustflags=("-Cno-vectorize-loops",)),
    Variant("rust-no-slp-vectorize", rustflags=("-Cno-vectorize-slp",)),
    Variant(
        "rust-symbolic-functions",
        rustflags=("-Clink-arg=-Wl,-Bsymbolic-functions",),
    ),
    Variant(
        "rust-x86-64-v2",
        rustflags=("-Ctarget-cpu=x86-64-v2",),
        portable=False,
    ),
    Variant(
        "rust-x86-64-v3",
        rustflags=("-Ctarget-cpu=x86-64-v3",),
        portable=False,
    ),
    Variant(
        "rust-native",
        rustflags=("-Ctarget-cpu=native",),
        portable=False,
    ),
    Variant(
        "rust-native-inline-450",
        rustflags=("-Ctarget-cpu=native", "-Cllvm-args=--inline-threshold=450"),
        portable=False,
    ),
    Variant(
        "rust-thin-native",
        rustflags=("-Ctarget-cpu=native",),
        profile=(("LTO", "thin"),),
        portable=False,
    ),
    Variant(
        "rust-thin-x86-64-v3",
        rustflags=("-Ctarget-cpu=x86-64-v3",),
        profile=(("LTO", "thin"),),
        portable=False,
    ),
    Variant("bridge-clang", compiler="clang"),
    Variant("bridge-clang-o2", compiler="clang", bridge_flags=("-O2",)),
    Variant("bridge-clang-lto", compiler="clang", bridge_flags=("-flto",)),
    Variant("bridge-clang-no-plt", compiler="clang", bridge_flags=("-fno-plt",)),
    Variant(
        "bridge-zig-cc",
        compiler="zig-cc",
        rustflags=("-Clink-arg=-Wl,-soname,_rust_engine.so",),
        bridge_flags=("-mcpu=baseline",),
    ),
    Variant(
        "bridge-zig-cc-lto",
        compiler="zig-cc",
        rustflags=("-Clink-arg=-Wl,-soname,_rust_engine.so",),
        bridge_flags=("-mcpu=baseline", "-flto"),
    ),
    Variant(
        "bridge-zig-cc-native",
        compiler="zig-cc",
        rustflags=("-Clink-arg=-Wl,-soname,_rust_engine.so",),
        portable=False,
    ),
    Variant("bridge-o2", bridge_flags=("-O2",)),
    Variant("bridge-gcc-lto", bridge_flags=("-flto",)),
    Variant("bridge-no-plt", bridge_flags=("-fno-plt",)),
    Variant(
        "bridge-no-interposition",
        bridge_flags=("-fno-semantic-interposition",),
    ),
    Variant("bridge-hidden", bridge_flags=("-fvisibility=hidden",)),
    Variant(
        "bridge-symbolic-functions",
        bridge_flags=("-Wl,-Bsymbolic-functions",),
    ),
    Variant(
        "bridge-native-tune",
        bridge_flags=("-mtune=native",),
    ),
    Variant(
        "bridge-native-arch",
        bridge_flags=("-march=native",),
        portable=False,
    ),
    Variant(
        "bridge-clang-no-interposition",
        compiler="clang",
        bridge_flags=("-fno-semantic-interposition",),
    ),
    Variant("bridge-static-rust", static_bridge=True),
    Variant(
        "bridge-static-strip-debug",
        bridge_flags=("-Wl,--strip-debug",),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-strip-all",
        bridge_flags=("-Wl,--strip-all",),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-gc",
        bridge_flags=("-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections"),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-gc-strip",
        bridge_flags=(
            "-ffunction-sections",
            "-fdata-sections",
            "-Wl,--gc-sections",
            "-Wl,--strip-all",
        ),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-hidden",
        bridge_flags=(
            "-fvisibility=hidden",
            "-ffunction-sections",
            "-fdata-sections",
            "-Wl,--gc-sections",
        ),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-clang",
        compiler="clang",
        bridge_flags=("-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections"),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-zig",
        compiler="zig-cc",
        bridge_flags=(
            "-mcpu=baseline",
            "-ffunction-sections",
            "-fdata-sections",
            "-Wl,--gc-sections",
            "-Wl,--strip-all",
        ),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-zig-lto",
        compiler="zig-cc",
        rustflags=("-Clinker-plugin-lto",),
        bridge_flags=(
            "-mcpu=baseline",
            "-flto",
            "-ffunction-sections",
            "-fdata-sections",
            "-Wl,--gc-sections",
            "-Wl,--strip-all",
        ),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-zig-native",
        compiler="zig-cc",
        bridge_flags=(
            "-ffunction-sections",
            "-fdata-sections",
            "-Wl,--gc-sections",
            "-Wl,--strip-all",
        ),
        static_bridge=True,
        portable=False,
    ),
    Variant(
        "bridge-static-thin",
        profile=(("LTO", "thin"),),
        bridge_flags=("-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections"),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-thin-strip",
        profile=(("LTO", "thin"),),
        bridge_flags=(
            "-ffunction-sections",
            "-fdata-sections",
            "-Wl,--gc-sections",
            "-Wl,--strip-all",
        ),
        static_bridge=True,
    ),
    Variant(
        "bridge-static-rust-native",
        rustflags=("-Ctarget-cpu=native",),
        static_bridge=True,
        portable=False,
    ),
    Variant(
        "bridge-static-gc-native",
        rustflags=("-Ctarget-cpu=native",),
        bridge_flags=("-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections"),
        static_bridge=True,
        portable=False,
    ),
    Variant(
        "bridge-static-gc-x86-64-v3",
        rustflags=("-Ctarget-cpu=x86-64-v3",),
        bridge_flags=("-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections"),
        static_bridge=True,
        portable=False,
    ),
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_variants(names: list[str] | None) -> list[Variant]:
    known = {variant.name: variant for variant in VARIANTS}
    if not names:
        return list(VARIANTS)
    selected: list[Variant] = []
    for item in names:
        for name in item.split(","):
            if name not in known:
                raise SystemExit(f"unknown build variant: {name}")
            if known[name] not in selected:
                selected.append(known[name])
    if known["baseline"] not in selected:
        selected.insert(0, known["baseline"])
    return selected


def prepare(workspace: Path, source_ref: str | None = None) -> dict:
    source_root = workspace / "source"
    rust_source = ROOT / "candidates" / "rust"
    wrapper_source = ROOT / "candidates" / "rust_candidate.py"
    watched = (
        *(
            path
            for path in sorted(rust_source.rglob("*"))
            if path.is_file()
            and "target" not in path.relative_to(rust_source).parts
            and "__pycache__" not in path.relative_to(rust_source).parts
        ),
        wrapper_source,
    )
    workspace.mkdir(parents=True, exist_ok=True)
    if source_root.exists():
        record = json.loads((workspace / "source-manifest.json").read_text())
        if record.get("source_ref") != source_ref:
            raise RuntimeError(
                "the requested source differs from the existing snapshot"
            )
        for relative, expected in record["snapshot_sha256"].items():
            if file_hash(source_root / relative) != expected:
                raise RuntimeError(f"isolated Rust source snapshot drifted: {relative}")
        return record
    source_root.mkdir()
    if source_ref is None:
        before = {str(path.relative_to(ROOT)): file_hash(path) for path in watched}
        shutil.copytree(
            rust_source,
            source_root / "rust",
            ignore=shutil.ignore_patterns("target", "__pycache__"),
        )
        shutil.copy2(wrapper_source, source_root / "rust_candidate.py")
        after = {str(path.relative_to(ROOT)): file_hash(path) for path in watched}
        if before != after:
            raise RuntimeError(
                "Rust sources changed during the isolated build snapshot"
            )
        source_commit = None
    else:
        revision = subprocess.run(
            ["git", "rev-parse", "--verify", source_ref + "^{commit}"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        source_commit = revision.stdout.strip()
        before = {}
        listing = subprocess.run(
            [
                "git",
                "ls-tree",
                "-r",
                "--name-only",
                source_commit,
                "--",
                "candidates/rust",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tracked = [
            relative
            for relative in listing.stdout.splitlines()
            if "/target/" not in relative and "/__pycache__/" not in relative
        ]
        tracked.append("candidates/rust_candidate.py")
        for relative in tracked:
            result = subprocess.run(
                ["git", "show", source_commit + ":" + relative],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if relative == "candidates/rust_candidate.py":
                destination = source_root / "rust_candidate.py"
            else:
                destination = source_root / Path(relative).relative_to("candidates")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(result.stdout)
            before[relative] = hashlib.sha256(result.stdout).hexdigest()
    snapshot_paths = {
        str(path.relative_to(source_root)): path
        for path in sorted(source_root.rglob("*"))
        if path.is_file()
    }
    record = {
        "schema": "rebar-rust-build-snapshot-v1",
        "root": str(ROOT),
        "workspace": str(workspace),
        "python": sys.version,
        "machine": platform.machine(),
        "source_ref": source_ref,
        "source_commit": source_commit,
        "production_sha256": before,
        "snapshot_sha256": {
            relative: file_hash(path) for relative, path in snapshot_paths.items()
        },
    }
    (workspace / "source-manifest.json").write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n"
    )
    return record


def engine_key(variant: Variant) -> str:
    payload = json.dumps(
        {
            "rustflags": variant.rustflags,
            "profile": variant.profile,
            "static_bridge": variant.static_bridge,
        },
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()[:20]


def checked_run(command: list[str], *, env: dict[str, str], cwd: Path) -> dict:
    started = time.perf_counter_ns()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    record = {
        "command": command,
        "returncode": result.returncode,
        "elapsed_ns": time.perf_counter_ns() - started,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode:
        raise RuntimeError(json.dumps(record, sort_keys=True))
    return record


def build_variant(workspace: Path, variant: Variant) -> dict:
    source_root = workspace / "source"
    variant_root = workspace / "variants" / variant.name
    package = variant_root / "candidates"
    package.mkdir(parents=True, exist_ok=True)
    extension_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    include = sysconfig.get_path("include")
    if not isinstance(extension_suffix, str) or not isinstance(include, str):
        raise RuntimeError("the active CPython extension configuration is missing")
    if variant.portable and any(
        flag.startswith("-Ctarget-cpu=")
        and flag not in {"-Ctarget-cpu=x86-64", "-Ctarget-cpu=generic"}
        for flag in variant.rustflags
    ):
        raise RuntimeError(
            f"CPU-specific Rust build was labeled portable: {variant.name}"
        )
    if variant.compiler == "zig-cc":
        if variant.portable and "-mcpu=baseline" not in variant.bridge_flags:
            raise RuntimeError(
                f"host-specialized Zig build was labeled portable: {variant.name}"
            )
        zig = os.environ.get("REBAR_ZIG") or shutil.which("zig")
        if zig is None:
            configured = Path("/tmp/rebar-design-survey/zig-0.16.0/zig")
            if configured.is_file():
                zig = str(configured)
        if zig is None:
            raise RuntimeError("Zig C compiler unavailable; set REBAR_ZIG")
        compiler_command = [zig, "cc"]
    else:
        compiler = shutil.which(variant.compiler)
        if compiler is None:
            raise RuntimeError(f"C compiler unavailable: {variant.compiler}")
        compiler_command = [compiler]
    if not variant.portable and platform.machine() not in {"x86_64", "AMD64"}:
        raise RuntimeError(f"x86-specific build unavailable: {variant.name}")

    target = workspace / "targets" / engine_key(variant)
    rust_library = target / "release" / "librebar_rust_continuation.so"
    rust_static = target / "release" / "librebar_rust_continuation.a"
    rust_command = [
        "cargo",
        "rustc" if variant.static_bridge else "build",
        "--manifest-path",
        str(source_root / "rust" / "Cargo.toml"),
        "--release",
        "--locked",
        "--offline",
        "--target-dir",
        str(target),
    ]
    if variant.static_bridge:
        rust_command.extend(("--", "--crate-type", "staticlib"))
    environment = os.environ.copy()
    if variant.compiler == "zig-cc":
        environment["ZIG_GLOBAL_CACHE_DIR"] = str(workspace / "zig-global-cache")
        environment["ZIG_LOCAL_CACHE_DIR"] = str(workspace / "zig-local-cache")
    environment.pop("RUSTFLAGS", None)
    for name in (
        "LTO",
        "OPT_LEVEL",
        "CODEGEN_UNITS",
        "PANIC",
        "DEBUG",
        "STRIP",
    ):
        environment.pop("CARGO_PROFILE_RELEASE_" + name, None)
    if variant.rustflags:
        environment["RUSTFLAGS"] = " ".join(variant.rustflags)
    for name, value in variant.profile:
        environment["CARGO_PROFILE_RELEASE_" + name] = value
    rust_build = checked_run(rust_command, env=environment, cwd=workspace)
    if not rust_library.is_file():
        raise RuntimeError(f"Rust build did not produce the engine: {rust_library}")
    if variant.static_bridge and not rust_static.is_file():
        rust_static = target / "release" / "deps" / "librebar_rust_continuation.a"
    if variant.static_bridge and not rust_static.is_file():
        raise RuntimeError(f"Rust build did not produce a static engine: {rust_static}")
    shutil.copy2(rust_library, package / "_rust_engine.so")
    shutil.copy2(source_root / "rust_candidate.py", package / "rust_candidate.py")

    bridge_output = package / ("_rust_bridge" + extension_suffix)
    bridge_command = [
        *compiler_command,
        "-std=c11",
        "-O3",
        "-fPIC",
        "-shared",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-I" + include,
        *variant.bridge_flags,
        str(source_root / "rust" / "py_bridge.c"),
    ]
    if variant.static_bridge and variant.compiler == "zig-cc":
        exports = variant_root / "bridge-exports.map"
        exports.write_text(
            "{\n  global: PyInit__rust_bridge;\n  local: *;\n};\n",
            encoding="utf-8",
        )
        bridge_command.extend(
            (
                str(rust_static),
                "-Wl,--version-script=" + str(exports),
                "-lgcc_s",
                "-ldl",
                "-lpthread",
                "-lm",
            )
        )
    elif variant.static_bridge:
        bridge_command.extend(
            (str(rust_static), "-Wl,--exclude-libs=ALL", "-ldl", "-lpthread", "-lm")
        )
    elif variant.compiler == "zig-cc":
        bridge_command.extend((str(package / "_rust_engine.so"), "-Wl,-rpath,$ORIGIN"))
    else:
        bridge_command.extend(
            ("-L" + str(package), "-l:_rust_engine.so", "-Wl,-rpath,$ORIGIN")
        )
    bridge_command.extend(("-o", str(bridge_output)))
    bridge_build = checked_run(bridge_command, env=environment, cwd=workspace)
    smoke_environment = environment.copy()
    smoke_environment["PYTHONPATH"] = os.pathsep.join((str(variant_root), str(ROOT)))
    smoke_command = [
        sys.executable,
        "-c",
        (
            "import candidates.rust_candidate as m; "
            "assert m.search(r'(?P<w>\\w+)-(\\d+)', 'x ab-12 y').groups() "
            "== ('ab', '12'); "
            "assert m.findall(rb'\\w+', b'a_b ! 12') == [b'a_b', b'12']; "
            "assert m.fullmatch(r'(?>a*)a', 'aaaa') is None"
        ),
    ]
    smoke = checked_run(smoke_command, env=smoke_environment, cwd=workspace)
    record = {
        "schema": "rebar-rust-build-variant-v1",
        "variant": asdict(variant),
        "package_root": str(variant_root),
        "engine_sha256": file_hash(package / "_rust_engine.so"),
        "engine_bytes": (package / "_rust_engine.so").stat().st_size,
        "bridge_sha256": file_hash(bridge_output),
        "bridge_bytes": bridge_output.stat().st_size,
        "rust_build": rust_build,
        "bridge_build": bridge_build,
        "import_smoke": smoke,
    }
    (variant_root / "build.json").write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n"
    )
    return record


def practice_cases(samples_per_category: int) -> tuple[object, list[tuple], dict]:
    from tools.perf_v6 import frozen

    suite, cases, expected, manifest = frozen()
    grouped: dict[str, list[tuple]] = defaultdict(list)
    for case, want in zip(cases, expected, strict=True):
        if case["cohort"] == "calibration":
            grouped[case["category"]].append((case, want))
    selected: list[tuple] = []
    for category in sorted(grouped):
        values = sorted(grouped[category], key=lambda pair: pair[0]["id"])
        if len(values) <= samples_per_category:
            indexes = range(len(values))
        elif samples_per_category == 1:
            indexes = (len(values) // 2,)
        else:
            indexes = (
                index * (len(values) - 1) // (samples_per_category - 1)
                for index in range(samples_per_category)
            )
        for index in indexes:
            selected.append(values[index])
    return suite, selected, manifest


def timed_case(
    module: object,
    suite: object,
    case: dict,
    expected: dict,
    variant: str,
    trial: int,
    max_ops: int,
    *,
    batch: int | None = None,
) -> dict:
    from tools.perf_v5 import digest, operation, snapshot
    from tools.perf_v6 import correctness_gate

    expected_digest = correctness_gate(module, case, expected)
    action = operation(module, case)
    for _ in range(suite.WARMUPS):
        action()
    operations = min(case["ops"], max_ops)
    enabled = gc.isenabled()
    if enabled:
        gc.disable()
    try:
        started = time.perf_counter_ns()
        result = None
        for _ in range(operations):
            result = action()
        elapsed = time.perf_counter_ns() - started
    finally:
        if enabled:
            gc.enable()
    actual = snapshot(result)
    if digest(actual) != expected_digest or actual != expected["result"]:
        raise RuntimeError(f"post-timing Rust build mismatch: {case['id']}")
    row = {
        "schema": "rebar-rust-build-row-v1",
        "variant": variant,
        "trial": trial,
        "case": case["id"],
        "category": case["category"],
        "api": case["api"],
        "lifecycle": case["lifecycle"],
        "cohort": case["cohort"],
        "ops": operations,
        "frozen_ops": case["ops"],
        "elapsed_ns": elapsed,
        "ns_per_op": elapsed / operations,
        "expected_sha256": expected_digest,
    }
    if batch is not None:
        row["schema"] = "rebar-rust-build-paired-row-v2"
        row["batch"] = batch
    return row


def isolated_module(package_root: Path) -> object:
    module = importlib.import_module("candidates.rust_candidate")
    module_path = Path(module.__file__).resolve()
    if not module_path.is_relative_to(package_root.resolve()):
        raise RuntimeError(f"isolated Rust module was not imported: {module_path}")
    bridge = importlib.import_module("candidates._rust_bridge")
    if not Path(bridge.__file__).resolve().is_relative_to(package_root.resolve()):
        raise RuntimeError("isolated Rust CPython bridge was not imported")
    return module


def worker(args: argparse.Namespace) -> None:
    suite, selected, manifest = practice_cases(args.samples_per_category)
    module = isolated_module(args.package_root)
    cases = list(selected)
    random.Random(ORDER_SEED + args.trial).shuffle(cases)
    rows = [
        timed_case(
            module, suite, case, expected, args.variant, args.trial, args.max_ops
        )
        for case, expected in cases
    ]
    print(
        json.dumps(
            {
                "schema": "rebar-rust-build-trial-v1",
                "variant": args.variant,
                "trial": args.trial,
                "frozen_expected_sha256": manifest["expected_sha256"],
                "checks": 2 * len(rows),
                "rows": rows,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def stream_worker(args: argparse.Namespace) -> None:
    suite, selected, manifest = practice_cases(args.samples_per_category)
    module = isolated_module(args.package_root)
    lookup = {case["id"]: (case, expected) for case, expected in selected}
    print(
        json.dumps(
            {
                "schema": "rebar-rust-build-stream-ready-v2",
                "variant": args.variant,
                "cases": len(lookup),
                "frozen_expected_sha256": manifest["expected_sha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        flush=True,
    )
    for line in sys.stdin:
        request = json.loads(line)
        if request.get("command") == "stop":
            return
        if request.get("command") != "measure":
            raise RuntimeError("unexpected isolated Rust worker command")
        pair = lookup.get(request.get("case"))
        if pair is None:
            raise RuntimeError("unfrozen or held-out case sent to build worker")
        row = timed_case(
            module,
            suite,
            pair[0],
            pair[1],
            args.variant,
            request["trial"],
            request["max_ops"],
            batch=request["batch"],
        )
        print(json.dumps(row, sort_keys=True, separators=(",", ":")), flush=True)


def start_stream(
    workspace: Path,
    variant: Variant,
    samples_per_category: int,
    expected_cases: int,
    frozen_hash: str,
) -> subprocess.Popen:
    package_root = workspace / "variants" / variant.name
    build_manifest = json.loads((package_root / "build.json").read_text())
    extension_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    if not isinstance(extension_suffix, str):
        raise RuntimeError("the active CPython extension suffix is missing")
    engine = package_root / "candidates" / "_rust_engine.so"
    bridge = package_root / "candidates" / ("_rust_bridge" + extension_suffix)
    if (
        build_manifest.get("variant", {}).get("name") != variant.name
        or file_hash(engine) != build_manifest.get("engine_sha256")
        or file_hash(bridge) != build_manifest.get("bridge_sha256")
    ):
        raise RuntimeError(f"isolated Rust build artifacts drifted: {variant.name}")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join((str(package_root), str(ROOT)))
    process = subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "stream-worker",
            "--package-root",
            str(package_root),
            "--variant",
            variant.name,
            "--samples-per-category",
            str(samples_per_category),
        ],
        cwd=workspace,
        env=environment,
        text=True,
        bufsize=1,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    line = process.stdout.readline()
    if not line:
        assert process.stderr is not None
        error = process.stderr.read()
        returncode = process.wait(timeout=30)
        failure = {
            "schema": "rebar-rust-build-worker-failure-v1",
            "variant": variant.name,
            "package_root": str(package_root),
            "returncode": returncode,
            "stderr": error,
            "engine_sha256": file_hash(engine),
            "bridge_sha256": file_hash(bridge),
        }
        failure_dir = workspace / "evidence"
        failure_dir.mkdir(parents=True, exist_ok=True)
        (failure_dir / ("worker-failure-" + variant.name + ".json")).write_text(
            json.dumps(failure, sort_keys=True, indent=2) + "\n"
        )
        raise RuntimeError(f"isolated Rust worker failed: {variant.name}: {error}")
    ready = json.loads(line)
    if (
        ready.get("schema") != "rebar-rust-build-stream-ready-v2"
        or ready.get("variant") != variant.name
        or ready.get("cases") != expected_cases
        or ready.get("frozen_expected_sha256") != frozen_hash
    ):
        process.terminate()
        process.wait(timeout=30)
        raise RuntimeError(f"isolated Rust worker metadata drifted: {variant.name}")
    return process


def paired_trials(
    workspace: Path,
    variants: list[Variant],
    trials: int,
    samples_per_category: int,
    max_ops: int,
    batch_size: int,
) -> Path:
    if batch_size < 2:
        raise ValueError("paired builds require at least two workers per batch")
    _, selected, manifest = practice_cases(samples_per_category)
    baseline = next((item for item in variants if item.name == "baseline"), None)
    if baseline is None:
        raise RuntimeError("paired build measurement has no baseline")
    challengers = [item for item in variants if item.name != "baseline"]
    if not challengers:
        raise RuntimeError("paired build measurement has no challenger")
    batches = [
        [baseline, *challengers[index : index + batch_size - 1]]
        for index in range(0, len(challengers), batch_size - 1)
    ]
    evidence = workspace / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    raw = evidence / "build-paired-raw.jsonl"
    with raw.open("w", encoding="utf-8") as destination:
        for batch_index, members in enumerate(batches):
            workers: dict[str, subprocess.Popen] = {}
            try:
                for member in members:
                    workers[member.name] = start_stream(
                        workspace,
                        member,
                        samples_per_category,
                        len(selected),
                        manifest["expected_sha256"],
                    )
                for trial in range(trials):
                    cases = list(selected)
                    random.Random(
                        ORDER_SEED + batch_index * 100003 + trial * 1009
                    ).shuffle(cases)
                    for case, expected in cases:
                        order = list(members)
                        random.Random(
                            ORDER_SEED
                            + batch_index * 100003
                            + trial * 1009
                            + sum(map(ord, case["id"]))
                        ).shuffle(order)
                        for member in order:
                            process = workers[member.name]
                            assert process.stdin is not None
                            assert process.stdout is not None
                            process.stdin.write(
                                json.dumps(
                                    {
                                        "command": "measure",
                                        "case": case["id"],
                                        "trial": trial,
                                        "batch": batch_index,
                                        "max_ops": max_ops,
                                    },
                                    separators=(",", ":"),
                                )
                                + "\n"
                            )
                            process.stdin.flush()
                            line = process.stdout.readline()
                            if not line:
                                assert process.stderr is not None
                                raise RuntimeError(
                                    f"Rust paired worker stopped: {member.name}: "
                                    f"{process.stderr.read()}"
                                )
                            row = json.loads(line)
                            if (
                                row.get("schema") != "rebar-rust-build-paired-row-v2"
                                or row.get("variant") != member.name
                                or row.get("trial") != trial
                                or row.get("batch") != batch_index
                                or row.get("case") != case["id"]
                                or row.get("cohort") != "calibration"
                                or row.get("expected_sha256")
                                != expected["result_sha256"]
                            ):
                                raise RuntimeError("paired Rust build row drifted")
                            destination.write(json.dumps(row, sort_keys=True) + "\n")
                        destination.flush()
                    print(
                        json.dumps(
                            {
                                "schema": "rebar-rust-build-paired-progress-v2",
                                "batch": batch_index,
                                "batches": len(batches),
                                "trial": trial,
                                "trials": trials,
                                "variants": [item.name for item in members],
                                "cases": len(cases),
                                "correctness_checks": 2 * len(cases) * len(members),
                            },
                            sort_keys=True,
                        ),
                        flush=True,
                    )
            finally:
                for process in workers.values():
                    if process.stdin is not None and process.poll() is None:
                        try:
                            process.stdin.write('{"command":"stop"}\n')
                            process.stdin.flush()
                            process.stdin.close()
                        except (BrokenPipeError, OSError):
                            pass
                for process in workers.values():
                    try:
                        returncode = process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        returncode = process.wait(timeout=30)
                    if returncode:
                        assert process.stderr is not None
                        raise RuntimeError(
                            f"paired Rust build worker exited {returncode}: "
                            f"{process.stderr.read()}"
                        )
    return raw


def run_trials(
    workspace: Path,
    variants: list[Variant],
    trials: int,
    samples_per_category: int,
    max_ops: int,
) -> Path:
    evidence = workspace / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    raw = evidence / "build-raw.jsonl"
    with raw.open("w", encoding="utf-8") as stream:
        for trial in range(trials):
            order = list(variants)
            random.Random(ORDER_SEED + trial).shuffle(order)
            for variant in order:
                package_root = workspace / "variants" / variant.name
                environment = os.environ.copy()
                environment["PYTHONPATH"] = os.pathsep.join(
                    (str(package_root), str(ROOT))
                )
                command = [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "worker",
                    "--package-root",
                    str(package_root),
                    "--variant",
                    variant.name,
                    "--trial",
                    str(trial),
                    "--samples-per-category",
                    str(samples_per_category),
                    "--max-ops",
                    str(max_ops),
                ]
                completed = subprocess.run(
                    command,
                    cwd=workspace,
                    env=environment,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if completed.returncode:
                    raise RuntimeError(
                        json.dumps(
                            {
                                "variant": variant.name,
                                "trial": trial,
                                "command": command,
                                "returncode": completed.returncode,
                                "stdout": completed.stdout,
                                "stderr": completed.stderr,
                            },
                            sort_keys=True,
                        )
                    )
                result = json.loads(completed.stdout)
                if result["variant"] != variant.name or result["trial"] != trial:
                    raise RuntimeError("isolated Rust trial metadata drifted")
                for row in result["rows"]:
                    stream.write(json.dumps(row, sort_keys=True) + "\n")
                stream.flush()
                print(
                    json.dumps(
                        {
                            "variant": variant.name,
                            "trial": trial,
                            "cases": len(result["rows"]),
                            "correctness_checks": result["checks"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    return raw


def train_profile(
    workspace: Path,
    variant_name: str,
    samples_per_category: int,
    max_ops: int,
    passes: int,
) -> dict:
    package_root = workspace / "variants" / variant_name
    if not (package_root / "build.json").is_file():
        raise RuntimeError(f"instrumented Rust build is missing: {variant_name}")
    evidence = workspace / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    completed_trials = []
    for trial in range(passes):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join((str(package_root), str(ROOT)))
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "worker",
            "--package-root",
            str(package_root),
            "--variant",
            variant_name,
            "--trial",
            str(trial),
            "--samples-per-category",
            str(samples_per_category),
            "--max-ops",
            str(max_ops),
        ]
        started = time.perf_counter_ns()
        process = subprocess.run(
            command,
            cwd=workspace,
            env=environment,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.returncode:
            raise RuntimeError(
                json.dumps(
                    {
                        "variant": variant_name,
                        "trial": trial,
                        "returncode": process.returncode,
                        "stdout": process.stdout,
                        "stderr": process.stderr,
                    },
                    sort_keys=True,
                )
            )
        result = json.loads(process.stdout)
        if result["variant"] != variant_name or result["trial"] != trial:
            raise RuntimeError("Rust profile-training trial metadata drifted")
        rows = result.pop("rows")
        result["cases"] = len(rows)
        result["categories"] = len({row["category"] for row in rows})
        result["elapsed_ns"] = time.perf_counter_ns() - started
        result["case_ids_sha256"] = hashlib.sha256(
            "\n".join(row["case"] for row in rows).encode()
        ).hexdigest()
        completed_trials.append(result)
    profile_directory = workspace / "profiles"
    profiles = []
    if profile_directory.exists():
        for profile in sorted(profile_directory.rglob("*.profraw")):
            profiles.append(
                {
                    "path": str(profile),
                    "sha256": file_hash(profile),
                    "bytes": profile.stat().st_size,
                }
            )
    result = {
        "schema": "rebar-rust-build-profile-training-v1",
        "variant": variant_name,
        "workspace": str(workspace),
        "passes": passes,
        "trials": completed_trials,
        "profiles": profiles,
    }
    (evidence / "profile-training.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    return result


def profile_header_experiment(source: Path, destination: Path) -> dict:
    """Preserve and explicitly label a raw-header compatibility experiment."""

    payload = bytearray(source.read_bytes())
    if len(payload) < 16:
        raise RuntimeError("the generated LLVM profile header is incomplete")
    magic, encoded_version = struct.unpack_from("<QQ", payload)
    if magic != 0xFF6C70726F667281:
        raise RuntimeError("the file is not a little-endian 64-bit LLVM raw profile")
    version = encoded_version & 0xFFFFFFFF
    if version != 10:
        raise RuntimeError(f"unexpected generated LLVM profile version: {version}")
    struct.pack_into("<Q", payload, 8, (encoded_version & ~0xFFFFFFFF) | 9)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    result = {
        "schema": "rebar-rust-build-profile-compatibility-experiment-v1",
        "original": str(source),
        "original_sha256": file_hash(source),
        "original_version": version,
        "experimental": str(destination),
        "experimental_sha256": file_hash(destination),
        "experimental_version": 9,
        "warning": (
            "Header compatibility is an experiment; use requires independent "
            "profile validation, complete correctness checks, and measured gains."
        ),
    }
    destination.with_suffix(".json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    return result


def merge_profile(
    workspace: Path,
    profile: Path,
    output: Path,
    tool: str,
    label: str,
) -> dict:
    merger = shutil.which(tool)
    if merger is None:
        raise RuntimeError(f"LLVM profile merger is unavailable: {tool}")
    if not profile.is_file():
        raise RuntimeError(f"LLVM raw profile is unavailable: {profile}")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [merger, "merge", "--sparse", "-o", str(output), str(profile)]
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        cwd=workspace,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    record = {
        "schema": "rebar-rust-build-profile-merge-v1",
        "label": label,
        "command": command,
        "input": str(profile),
        "input_sha256": file_hash(profile),
        "output": str(output),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "elapsed_ns": time.perf_counter_ns() - started,
    }
    if output.is_file():
        record["output_sha256"] = file_hash(output)
        record["output_bytes"] = output.stat().st_size
    evidence = workspace / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in label
    )
    (evidence / ("profile-merge-" + safe_label + ".json")).write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n"
    )
    return record


def describe_regression(case: dict, log_speedup: float) -> dict:
    """Preserve the exact frozen workload responsible for a real slowdown."""

    speedup = math.exp(log_speedup)
    if speedup >= 1.0 / REGRESSION_SLOWDOWN_RATIO:
        raise RuntimeError("a nonregressing practice case was reported as a slowdown")
    return {
        "case": case["id"],
        "category": case["category"],
        "api": case["api"],
        "lifecycle": case["lifecycle"],
        "cohort": case["cohort"],
        "speedup": speedup,
        "slowdown": 1.0 / speedup,
    }


def validate_recorded_regressions(summary: dict, label: str) -> None:
    """Reject omitted, duplicate, mislabeled, or mathematically invalid losses."""

    threshold = 1.0 / REGRESSION_SLOWDOWN_RATIO
    if summary.get("regression_speedup_threshold") != threshold:
        raise RuntimeError(f"the {label} uses the wrong 20% slowdown threshold")
    for item in summary.get("variants", []):
        details = item.get("regression_cases")
        if not isinstance(details, list) or len(details) != item.get(
            "regressions_gt_20pct"
        ):
            raise RuntimeError(
                f"the {label} hides slowdown cases for {item['variant']}"
            )
        seen = set()
        for detail in details:
            if (
                not isinstance(detail, dict)
                or detail.get("cohort") != "calibration"
                or detail.get("category") not in item["categories"]
                or not isinstance(detail.get("case"), str)
                or detail["case"] in seen
                or not isinstance(detail.get("speedup"), (int, float))
                or not 0 < detail["speedup"] < threshold
                or not isinstance(detail.get("slowdown"), (int, float))
                or not math.isclose(
                    detail["slowdown"] * detail["speedup"],
                    1.0,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                )
            ):
                raise RuntimeError(
                    f"the {label} contains an invalid slowdown: {item['variant']}"
                )
            seen.add(detail["case"])


def summarize_paired(
    workspace: Path,
    trials: int,
    samples_per_category: int,
    bootstraps: int,
    max_ops: int,
    batch_size: int,
    attempted_variants: int | None = None,
    build_failures: list[dict] | None = None,
) -> dict:
    suite, selected, manifest = practice_cases(samples_per_category)
    selected_ids = {case["id"] for case, _ in selected}
    selected_cases = {case["id"]: case for case, _ in selected}
    expected_hashes = {
        case["id"]: expected["result_sha256"] for case, expected in selected
    }
    categories = {case["id"]: case["category"] for case, _ in selected}
    raw = workspace / "evidence" / "build-paired-raw.jsonl"
    records: dict[str, dict[int, dict[str, dict[int, float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))
    )
    rows = 0
    with raw.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if (
                row.get("schema") != "rebar-rust-build-paired-row-v2"
                or row.get("cohort") != "calibration"
                or row.get("case") not in selected_ids
                or row.get("expected_sha256") != expected_hashes.get(row.get("case"))
                or row.get("ops") != min(row.get("frozen_ops", 0), max_ops)
            ):
                raise RuntimeError("unfrozen or incorrect paired Rust build row")
            bucket = records[row["variant"]][row["batch"]][row["case"]]
            if row["trial"] in bucket:
                raise RuntimeError("duplicate paired Rust build measurement")
            bucket[row["trial"]] = row["ns_per_op"]
            rows += 1
    if "baseline" not in records:
        raise RuntimeError("paired Rust build pilot has no baseline")
    baseline_batches = records["baseline"]
    results = []
    for name, batches in sorted(records.items()):
        if name == "baseline":
            build_record = json.loads(
                (workspace / "variants" / name / "build.json").read_text()
            )
            results.append(
                {
                    "variant": name,
                    "portable": build_record["variant"]["portable"],
                    "static_bridge": build_record["variant"]["static_bridge"],
                    "cases": len(selected),
                    "trials": trials,
                    "batches": len(batches),
                    "speedup_vs_current_build": 1.0,
                    "ci95_low": 1.0,
                    "ci95_high": 1.0,
                    "faster_cases": 0,
                    "regressions_gt_20pct": 0,
                    "regression_cases": [],
                    "engine_bytes": build_record["engine_bytes"],
                    "bridge_bytes": build_record["bridge_bytes"],
                    "categories": {
                        category: 1.0 for category in sorted(set(categories.values()))
                    },
                }
            )
            continue
        if len(batches) != 1:
            raise RuntimeError(
                f"Rust build variant belongs to multiple batches: {name}"
            )
        batch, cases = next(iter(batches.items()))
        if batch not in baseline_batches:
            raise RuntimeError(f"paired Rust build baseline missing: {name}")
        baseline = baseline_batches[batch]
        if set(cases) != selected_ids or set(baseline) != selected_ids:
            raise RuntimeError(f"paired Rust build cases differ: {name}")
        paired_logs = []
        category_logs: dict[str, list[float]] = defaultdict(list)
        for case_id in sorted(selected_ids):
            measured = cases[case_id]
            reference = baseline[case_id]
            if set(measured) != set(range(trials)) or set(reference) != set(
                range(trials)
            ):
                raise RuntimeError(
                    f"paired Rust build trials differ: {name}: {case_id}"
                )
            values = tuple(
                math.log(reference[trial] / measured[trial]) for trial in range(trials)
            )
            paired_logs.append(values)
            category_logs[categories[case_id]].append(statistics.fmean(values))
        case_logs = [statistics.fmean(values) for values in paired_logs]
        regression_cases = [
            describe_regression(selected_cases[case_id], value)
            for case_id, value in zip(sorted(selected_ids), case_logs, strict=True)
            if math.exp(value) < 1.0 / REGRESSION_SLOWDOWN_RATIO
        ]
        random_source = random.Random(BOOTSTRAP_SEED + sum(map(ord, name)))
        draws = []
        for _ in range(bootstraps):
            draw = [
                paired_logs[random_source.randrange(len(paired_logs))][
                    random_source.randrange(trials)
                ]
                for _ in paired_logs
            ]
            draws.append(math.exp(statistics.fmean(draw)))
        draws.sort()
        build_record = json.loads(
            (workspace / "variants" / name / "build.json").read_text()
        )
        results.append(
            {
                "variant": name,
                "portable": build_record["variant"]["portable"],
                "static_bridge": build_record["variant"]["static_bridge"],
                "cases": len(case_logs),
                "trials": trials,
                "batches": 1,
                "batch": batch,
                "speedup_vs_current_build": math.exp(statistics.fmean(case_logs)),
                "ci95_low": draws[int((len(draws) - 1) * 0.025)],
                "ci95_high": draws[int((len(draws) - 1) * 0.975)],
                "faster_cases": sum(value > 0 for value in case_logs),
                "regressions_gt_20pct": len(regression_cases),
                "regression_cases": regression_cases,
                "engine_bytes": build_record["engine_bytes"],
                "bridge_bytes": build_record["bridge_bytes"],
                "categories": {
                    category: math.exp(statistics.fmean(values))
                    for category, values in sorted(category_logs.items())
                },
            }
        )
    results.sort(key=lambda item: item["speedup_vs_current_build"], reverse=True)
    failed = build_failures or []
    attempted = attempted_variants if attempted_variants is not None else len(results)
    if attempted != len(results) + len(failed):
        raise RuntimeError("Rust build variant denominator changed")
    result = {
        "schema": "rebar-rust-build-paired-summary-v2",
        "pairing": "randomized adjacent variants for every identical case and trial",
        "interval": "joint deterministic case-and-trial bootstrap",
        "regression_definition": (
            "candidate elapsed time is more than 1.2 times paired baseline elapsed time"
        ),
        "regression_speedup_threshold": 1.0 / REGRESSION_SLOWDOWN_RATIO,
        "frozen_expected_sha256": manifest["expected_sha256"],
        "raw_sha256": file_hash(raw),
        "source_snapshot": json.loads((workspace / "source-manifest.json").read_text()),
        "rows": rows,
        "attempted_variants": attempted,
        "correctness_qualified_variants": len(results),
        "build_failures": failed,
        "trials": trials,
        "samples_per_category": samples_per_category,
        "cases_per_variant": len(selected),
        "maximum_operations_per_case": max_ops,
        "warmups": suite.WARMUPS,
        "maximum_workers_per_batch": batch_size,
        "bootstraps": bootstraps,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "variants": results,
    }
    destination = workspace / "evidence" / "build-paired-summary.json"
    destination.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def regression_threshold_self_test() -> dict:
    """Prove that slowdowns between 20% and 25% cannot disappear."""

    samples = []
    for slowdown in (1.0, 1.19, 1.2, 1.2000001, 1.21, 1.24, 1.25, 1.2500001):
        speedup = 1.0 / slowdown
        actual = speedup < 1.0 / REGRESSION_SLOWDOWN_RATIO
        expected = slowdown > REGRESSION_SLOWDOWN_RATIO
        if actual != expected:
            raise RuntimeError(f"the 20% slowdown boundary is incorrect: {slowdown}")
        samples.append(
            {
                "slowdown": slowdown,
                "speedup": speedup,
                "is_over_20_percent_slower": actual,
                "old_incorrect_threshold_flags": speedup < 0.8,
            }
        )
    if not any(
        item["is_over_20_percent_slower"] and not item["old_incorrect_threshold_flags"]
        for item in samples
    ):
        raise RuntimeError("the 20% to 25% reporting blind spot was not tested")
    return {
        "schema": "rebar-rust-build-regression-threshold-self-test-v1",
        "regression_slowdown_ratio": REGRESSION_SLOWDOWN_RATIO,
        "regression_speedup_threshold": 1.0 / REGRESSION_SLOWDOWN_RATIO,
        "samples": samples,
        "result": "pass",
    }


def reclassify_paired_regressions(workspace: Path) -> dict:
    """Correct slowdown labels from preserved paired rows without rerunning timings."""

    evidence = workspace / "evidence"
    summary_path = evidence / "build-paired-summary.json"
    raw_path = evidence / "build-paired-raw.jsonl"
    snapshot_path = workspace / "source-manifest.json"
    if (
        not summary_path.is_file()
        or not raw_path.is_file()
        or not snapshot_path.is_file()
    ):
        raise RuntimeError("a complete paired build experiment is required")

    previous_text = summary_path.read_text(encoding="utf-8")
    summary = json.loads(previous_text)
    if (
        summary.get("schema") != "rebar-rust-build-paired-summary-v2"
        or summary.get("raw_sha256") != file_hash(raw_path)
        or summary.get("source_snapshot")
        != json.loads(snapshot_path.read_text(encoding="utf-8"))
    ):
        raise RuntimeError("paired build evidence or its source snapshot changed")

    correct_threshold = 1.0 / REGRESSION_SLOWDOWN_RATIO
    threshold_is_correct = (
        summary.get("regression_speedup_threshold") == correct_threshold
    )
    details_are_complete = all(
        isinstance(item.get("regression_cases"), list)
        and len(item["regression_cases"]) == item["regressions_gt_20pct"]
        for item in summary["variants"]
    )
    if threshold_is_correct and details_are_complete:
        return {
            "schema": "rebar-rust-build-regression-reclassification-v1",
            "workspace": str(workspace),
            "status": "already-correct",
            "rows": summary["rows"],
            "variants": len(summary["variants"]),
            "regression_speedup_threshold": correct_threshold,
        }
    if (
        not threshold_is_correct
        and summary.get("regression_speedup_threshold", 0.8) != 0.8
    ):
        raise RuntimeError("the previous build slowdown threshold is unrecognized")

    sample_count = summary.get("samples_per_category")
    if sample_count is None:
        baseline = next(
            (item for item in summary["variants"] if item.get("variant") == "baseline"),
            None,
        )
        if baseline is None or not isinstance(baseline.get("cases"), int):
            raise RuntimeError("a legacy paired build has no frozen case denominator")
        exact_samples = []
        for candidate_count in range(1, 17):
            _candidate_suite, candidate_cases, candidate_manifest = practice_cases(
                candidate_count
            )
            if (
                len(candidate_cases) == baseline["cases"]
                and candidate_manifest["expected_sha256"]
                == summary["frozen_expected_sha256"]
            ):
                exact_samples.append(candidate_count)
            if len(candidate_cases) > baseline["cases"]:
                break
        if len(exact_samples) != 1:
            raise RuntimeError("legacy frozen practice sample count is ambiguous")
        sample_count = exact_samples[0]
        summary["samples_per_category"] = sample_count
        summary["cases_per_variant"] = baseline["cases"]
    _suite, selected, manifest = practice_cases(sample_count)
    if summary.get("frozen_expected_sha256") != manifest["expected_sha256"]:
        raise RuntimeError("frozen practice-case answers changed")
    selected_ids = {case["id"] for case, _expected in selected}
    selected_cases = {case["id"]: case for case, _expected in selected}
    expected_hashes = {
        case["id"]: expected["result_sha256"] for case, expected in selected
    }
    trials = summary["trials"]
    allowed = {item["variant"] for item in summary["variants"]}
    if "baseline" not in allowed:
        raise RuntimeError("the paired build experiment has no baseline")
    max_operations = summary.get("maximum_operations_per_case")
    if max_operations is None:
        with raw_path.open(encoding="utf-8") as inputs:
            first = inputs.readline()
        if not first:
            raise RuntimeError("a legacy paired build has no raw measurements")
        first_row = json.loads(first)
        if not (
            isinstance(first_row.get("ops"), int)
            and isinstance(first_row.get("frozen_ops"), int)
            and 0 < first_row["ops"] < first_row["frozen_ops"]
        ):
            raise RuntimeError(
                "legacy paired operation limit is not independently provable"
            )
        max_operations = first_row["ops"]
        summary["maximum_operations_per_case"] = max_operations

    baseline_times: dict[tuple[int, str, int], float] = {}
    challenger_times: dict[tuple[str, int, str, int], float] = {}
    rows = 0
    with raw_path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if (
                row.get("schema") != "rebar-rust-build-paired-row-v2"
                or row.get("cohort") != "calibration"
                or row.get("variant") not in allowed
                or row.get("case") not in selected_ids
                or row.get("expected_sha256") != expected_hashes.get(row.get("case"))
                or row.get("ops") != min(row.get("frozen_ops", 0), max_operations)
                or not isinstance(row.get("trial"), int)
                or not 0 <= row["trial"] < trials
                or not isinstance(row.get("batch"), int)
                or not isinstance(row.get("ns_per_op"), (float, int))
                or row["ns_per_op"] <= 0
            ):
                raise RuntimeError("an invalid or unfrozen paired build row was found")
            if row["variant"] == "baseline":
                reference_key = (row["batch"], row["case"], row["trial"])
                if reference_key in baseline_times:
                    raise RuntimeError("a paired baseline trial appears more than once")
                baseline_times[reference_key] = row["ns_per_op"]
            else:
                challenger_key = (
                    row["variant"],
                    row["batch"],
                    row["case"],
                    row["trial"],
                )
                if challenger_key in challenger_times:
                    raise RuntimeError("a paired build trial appears more than once")
                challenger_times[challenger_key] = row["ns_per_op"]
            rows += 1
    if rows != summary["rows"]:
        raise RuntimeError("the number of paired raw build timings changed")

    cutoff_log = math.log(correct_threshold)
    changed = 0
    for item in summary["variants"]:
        if item["variant"] == "baseline":
            if item["regressions_gt_20pct"] != 0:
                raise RuntimeError("the build baseline cannot regress against itself")
            item["regression_cases"] = []
            continue
        if item.get("cases") != len(selected_ids) or item.get("trials") != trials:
            raise RuntimeError("paired build case or trial counts changed")
        batch = item.get("batch")
        if not isinstance(batch, int):
            raise RuntimeError("a paired build challenger has no recorded batch")
        values = []
        regression_cases = []
        for case_id in sorted(selected_ids):
            paired_values = []
            for trial in range(trials):
                reference_key = (batch, case_id, trial)
                challenger_key = (item["variant"], batch, case_id, trial)
                if (
                    reference_key not in baseline_times
                    or challenger_key not in challenger_times
                ):
                    raise RuntimeError(
                        "paired build trials or baselines are incomplete"
                    )
                paired_values.append(
                    math.log(
                        baseline_times[reference_key] / challenger_times[challenger_key]
                    )
                )
            value = statistics.fmean(paired_values)
            values.append(value)
            if value < cutoff_log:
                regression_cases.append(
                    describe_regression(selected_cases[case_id], value)
                )
        speed = math.exp(statistics.fmean(values))
        if not math.isclose(
            speed,
            item["speedup_vs_current_build"],
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise RuntimeError("a recorded paired build speed changed")
        if sum(value > 0 for value in values) != item["faster_cases"]:
            raise RuntimeError("a recorded paired faster-case count changed")
        corrected = len(regression_cases)
        if corrected != item["regressions_gt_20pct"]:
            changed += 1
        item["regressions_gt_20pct"] = corrected
        item["regression_cases"] = regression_cases

    existing_correction = summary.get("regression_threshold_correction")
    if existing_correction is not None:
        previous_path = evidence / existing_correction["previous_summary_file"]
        previous_hash = existing_correction["previous_summary_sha256"]
        if not previous_path.is_file() or file_hash(previous_path) != previous_hash:
            raise RuntimeError("the original pre-correction summary was not preserved")
        changed = existing_correction["changed_variants"]
    else:
        previous_hash = hashlib.sha256(previous_text.encode("utf-8")).hexdigest()
        previous_path = (
            evidence / "build-paired-summary-pre-regression-threshold-fix.json"
        )
        if previous_path.exists():
            if file_hash(previous_path) != previous_hash:
                raise RuntimeError("an existing pre-correction build summary differs")
        else:
            previous_path.write_text(previous_text, encoding="utf-8")
    summary["regression_definition"] = (
        "candidate elapsed time is more than 1.2 times paired baseline elapsed time"
    )
    summary["regression_speedup_threshold"] = correct_threshold
    summary["regression_threshold_correction"] = {
        "previous_summary_file": previous_path.name,
        "previous_summary_sha256": previous_hash,
        "previous_speedup_threshold": 0.8,
        "correct_speedup_threshold": correct_threshold,
        "changed_variants": changed,
        "raw_sha256": summary["raw_sha256"],
        "method": "reclassify every original paired raw case without new timings",
        "every_regression_case_preserved": True,
    }
    summary_path.write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "schema": "rebar-rust-build-regression-reclassification-v1",
        "workspace": str(workspace),
        "status": "corrected",
        "rows": rows,
        "variants": len(summary["variants"]),
        "changed_variants": changed,
        "previous_summary_sha256": previous_hash,
        "regression_speedup_threshold": correct_threshold,
    }


def summarize(workspace: Path, trials: int, bootstraps: int) -> dict:
    raw = workspace / "evidence" / "build-raw.jsonl"
    records: dict[str, dict[str, dict[int, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    case_categories: dict[str, str] = {}
    row_count = 0
    with raw.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["schema"] != "rebar-rust-build-row-v1":
                raise RuntimeError("unexpected Rust build measurement schema")
            if row["cohort"] != "calibration":
                raise RuntimeError("held-out cases entered a build-selection pilot")
            bucket = records[row["variant"]][row["case"]]
            if row["trial"] in bucket:
                raise RuntimeError("duplicate Rust build measurement")
            bucket[row["trial"]] = row["ns_per_op"]
            case_categories[row["case"]] = row["category"]
            row_count += 1
    if "baseline" not in records:
        raise RuntimeError("build pilot has no baseline")
    baseline = records["baseline"]
    results = []
    for name, cases in sorted(records.items()):
        if set(cases) != set(baseline):
            raise RuntimeError(f"Rust build cases differ for {name}")
        case_logs = []
        category_logs: dict[str, list[float]] = defaultdict(list)
        for case in sorted(cases):
            measured = cases[case]
            reference = baseline[case]
            if set(measured) != set(range(trials)):
                raise RuntimeError(f"Rust build trial count drifted: {name}: {case}")
            if set(reference) != set(range(trials)):
                raise RuntimeError(f"Rust baseline trial count drifted: {case}")
            log_ratio = statistics.fmean(
                math.log(reference[trial] / measured[trial]) for trial in range(trials)
            )
            case_logs.append(log_ratio)
            category_logs[case_categories[case]].append(log_ratio)
        draws = []
        random_source = random.Random(BOOTSTRAP_SEED + sum(map(ord, name)))
        for _ in range(bootstraps):
            draws.append(
                math.exp(
                    statistics.fmean(
                        case_logs[random_source.randrange(len(case_logs))]
                        for _ in case_logs
                    )
                )
            )
        draws.sort()
        build_record = json.loads(
            (workspace / "variants" / name / "build.json").read_text()
        )
        results.append(
            {
                "variant": name,
                "portable": build_record["variant"]["portable"],
                "static_bridge": build_record["variant"]["static_bridge"],
                "cases": len(case_logs),
                "trials": trials,
                "speedup_vs_current_build": math.exp(statistics.fmean(case_logs)),
                "ci95_low": draws[int((len(draws) - 1) * 0.025)],
                "ci95_high": draws[int((len(draws) - 1) * 0.975)],
                "faster_cases": sum(value > 0 for value in case_logs),
                "regressions_gt_20pct": sum(
                    math.exp(value) < 1.0 / REGRESSION_SLOWDOWN_RATIO
                    for value in case_logs
                ),
                "engine_bytes": build_record["engine_bytes"],
                "bridge_bytes": build_record["bridge_bytes"],
                "categories": {
                    category: math.exp(statistics.fmean(values))
                    for category, values in sorted(category_logs.items())
                },
            }
        )
    results.sort(key=lambda item: item["speedup_vs_current_build"], reverse=True)
    output = {
        "schema": "rebar-rust-build-summary-v1",
        "regression_definition": (
            "candidate elapsed time is more than 1.2 times baseline elapsed time"
        ),
        "regression_speedup_threshold": 1.0 / REGRESSION_SLOWDOWN_RATIO,
        "raw_sha256": file_hash(raw),
        "source_snapshot": json.loads((workspace / "source-manifest.json").read_text()),
        "rows": row_count,
        "trials": trials,
        "bootstraps": bootstraps,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "variants": results,
    }
    destination = workspace / "evidence" / "build-summary.json"
    destination.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    return output


def export_lab(
    workspace: Path,
    destination: Path,
    unpaired_workspaces: list[Path],
    cross_workspaces: list[Path],
    profile_workspace: Path | None,
    finalist_workspace: Path | None = None,
) -> dict:
    evidence = workspace / "evidence"
    summary_path = evidence / "build-paired-summary.json"
    raw_path = evidence / "build-paired-raw.jsonl"
    if not summary_path.is_file() or not raw_path.is_file():
        raise RuntimeError("a complete, genuinely paired Rust build result is required")
    final = json.loads(summary_path.read_text())
    if final.get("schema") != "rebar-rust-build-paired-summary-v2" or final.get(
        "raw_sha256"
    ) != file_hash(raw_path):
        raise RuntimeError(
            "the final paired Rust build evidence is incomplete or changed"
        )
    source_manifest = workspace / "source-manifest.json"
    if not source_manifest.is_file() or final.get("source_snapshot") != json.loads(
        source_manifest.read_text()
    ):
        raise RuntimeError("the original Rust build source snapshot changed")
    correct_threshold = 1.0 / REGRESSION_SLOWDOWN_RATIO
    validate_recorded_regressions(final, "main paired build experiment")
    rejected_threshold_summary: dict | None = None
    correction = final.get("regression_threshold_correction")
    if correction is not None:
        previous = evidence / correction["previous_summary_file"]
        if (
            not previous.is_file()
            or file_hash(previous) != correction["previous_summary_sha256"]
        ):
            raise RuntimeError("the original build slowdown summary was not preserved")
        rejected_threshold_summary = json.loads(previous.read_text())
        if rejected_threshold_summary.get("raw_sha256") != final["raw_sha256"]:
            raise RuntimeError("the preserved slowdown summary used different timings")

    finalist: dict | None = None
    finalist_raw_path: Path | None = None
    finalist_records: dict[str, dict] = {}
    if finalist_workspace is not None:
        finalist_evidence = finalist_workspace / "evidence"
        finalist_summary_path = finalist_evidence / "build-paired-summary.json"
        finalist_raw_path = finalist_evidence / "build-paired-raw.jsonl"
        finalist_manifest = finalist_workspace / "source-manifest.json"
        if (
            not finalist_summary_path.is_file()
            or not finalist_raw_path.is_file()
            or not finalist_manifest.is_file()
        ):
            raise RuntimeError("the patched-engine finalist comparison is incomplete")
        finalist = json.loads(finalist_summary_path.read_text())
        if (
            finalist.get("schema") != "rebar-rust-build-paired-summary-v2"
            or finalist.get("raw_sha256") != file_hash(finalist_raw_path)
            or finalist.get("source_snapshot")
            != json.loads(finalist_manifest.read_text())
        ):
            raise RuntimeError("the patched-engine finalist evidence changed")
        if finalist.get("frozen_expected_sha256") != final.get(
            "frozen_expected_sha256"
        ):
            raise RuntimeError(
                "the patched-engine finalist comparison used different practice cases"
            )
        validate_recorded_regressions(finalist, "patched-engine finalist comparison")
        for item in finalist.get("variants", []):
            build = finalist_workspace / "variants" / item["variant"] / "build.json"
            if not build.is_file():
                raise RuntimeError(
                    "patched-engine finalist build metadata is missing: "
                    + item["variant"]
                )
            record = json.loads(build.read_text())
            settings = record["variant"]
            if item["portable"] != settings["portable"]:
                raise RuntimeError(
                    "patched-engine finalist portability metadata changed: "
                    + item["variant"]
                )
            if (
                item["portable"]
                and settings["compiler"] == "zig-cc"
                and "-mcpu=baseline" not in settings["bridge_flags"]
            ):
                raise RuntimeError(
                    "a host-specific Zig build entered patched finalist results: "
                    + item["variant"]
                )
            finalist_records[item["variant"]] = record
        if "baseline" not in finalist_records:
            raise RuntimeError("the patched-engine finalist comparison has no baseline")

    rejected = []
    for old_workspace in unpaired_workspaces:
        old_summary = old_workspace / "evidence" / "build-summary.json"
        old_raw = old_workspace / "evidence" / "build-raw.jsonl"
        if not old_summary.is_file() or not old_raw.is_file():
            raise RuntimeError(
                f"the rejected build pilot is incomplete: {old_workspace}"
            )
        data = json.loads(old_summary.read_text())
        if data.get("raw_sha256") != file_hash(old_raw):
            raise RuntimeError(f"a rejected Rust build pilot changed: {old_workspace}")
        rejected.append(
            {
                "label": old_workspace.name,
                "reason": (
                    "Rejected: each variant ran as a time-separated block; "
                    "CPU drift was not represented by its case-only intervals."
                ),
                "summary": data,
                "raw_path": old_raw,
            }
        )

    cross = []
    cross_paired = []
    for cross_workspace in cross_workspaces:
        for name in ("build-failures.json", "paired-build-failures.json"):
            failure = cross_workspace / name
            if failure.is_file():
                cross.append(
                    {
                        "label": cross_workspace.name,
                        "file": name,
                        "sha256": file_hash(failure),
                        "failures": json.loads(failure.read_text()),
                    }
                )
        paired_summary = cross_workspace / "evidence" / "build-paired-summary.json"
        paired_raw = cross_workspace / "evidence" / "build-paired-raw.jsonl"
        if paired_summary.is_file() and paired_raw.is_file():
            data = json.loads(paired_summary.read_text())
            if data.get("raw_sha256") != file_hash(paired_raw):
                raise RuntimeError(
                    f"cross-language paired measurement changed: {cross_workspace}"
                )
            qualification_issues = []
            cross_previous_summary = None
            if data.get("regression_speedup_threshold") != correct_threshold:
                qualification_issues.append(
                    "20% slowdowns were not counted at speedup below 1 / 1.2"
                )
            else:
                try:
                    validate_recorded_regressions(
                        data,
                        "cross-language comparison " + cross_workspace.name,
                    )
                except RuntimeError as error:
                    qualification_issues.append(str(error))
            cross_correction = data.get("regression_threshold_correction")
            if cross_correction is not None:
                previous = (
                    paired_summary.parent / cross_correction["previous_summary_file"]
                )
                if (
                    not previous.is_file()
                    or file_hash(previous)
                    != cross_correction["previous_summary_sha256"]
                ):
                    raise RuntimeError(
                        "a prior cross-language slowdown summary was not preserved"
                    )
                cross_previous_summary = json.loads(previous.read_text())
                if cross_previous_summary.get("raw_sha256") != data["raw_sha256"]:
                    raise RuntimeError(
                        "a prior cross-language slowdown summary used different rows"
                    )
            for result in data.get("variants", []):
                build = cross_workspace / "variants" / result["variant"] / "build.json"
                if not build.is_file():
                    qualification_issues.append(
                        f"missing build metadata: {result['variant']}"
                    )
                    continue
                settings = json.loads(build.read_text())["variant"]
                if (
                    settings.get("compiler") == "zig-cc"
                    and result.get("portable")
                    and "-mcpu=baseline" not in settings.get("bridge_flags", [])
                ):
                    qualification_issues.append(
                        "host-specific Zig build mislabeled portable: "
                        + result["variant"]
                    )
            cross_paired.append(
                {
                    "label": cross_workspace.name,
                    "summary": data,
                    "raw_path": paired_raw,
                    "qualification": (
                        "rejected" if qualification_issues else "accepted"
                    ),
                    "qualification_issues": qualification_issues,
                    "previous_threshold_summary": cross_previous_summary,
                }
            )
        worker_evidence = cross_workspace / "evidence"
        if worker_evidence.is_dir():
            for failure in sorted(worker_evidence.glob("worker-failure-*.json")):
                cross.append(
                    {
                        "label": cross_workspace.name,
                        "file": str(failure.relative_to(cross_workspace)),
                        "sha256": file_hash(failure),
                        "failure": json.loads(failure.read_text()),
                    }
                )

    profiles: dict = {}
    if profile_workspace is not None:
        profile_evidence = profile_workspace / "evidence"
        training = profile_evidence / "profile-training.json"
        if not training.is_file():
            raise RuntimeError("Rust profile-guided training evidence is missing")
        profiles["training"] = json.loads(training.read_text())
        profiles["merge_experiments"] = [
            json.loads(path.read_text())
            for path in sorted(profile_evidence.glob("profile-merge-*.json"))
        ]
        profiles["raw_profiles"] = []
        for item in profiles["training"].get("profiles", []):
            profile = Path(item["path"])
            if not profile.is_file() or file_hash(profile) != item["sha256"]:
                raise RuntimeError("generated Rust profile evidence changed")
            profiles["raw_profiles"].append(
                {
                    "name": profile.name,
                    "sha256": item["sha256"],
                    "base64": base64.b64encode(profile.read_bytes()).decode("ascii"),
                }
            )
        compatibility = profile_workspace / "profiles" / "experimental-v9.json"
        if compatibility.is_file():
            profiles["header_experiment"] = json.loads(compatibility.read_text())

    variant_records = {}
    for item in final["variants"]:
        build = workspace / "variants" / item["variant"] / "build.json"
        if not build.is_file():
            raise RuntimeError(
                f"final Rust build metadata is missing: {item['variant']}"
            )
        record = json.loads(build.read_text())
        settings = record["variant"]
        if item["portable"] != settings["portable"]:
            raise RuntimeError(
                f"Rust build portability metadata changed: {item['variant']}"
            )
        if (
            item["portable"]
            and settings["compiler"] == "zig-cc"
            and "-mcpu=baseline" not in settings["bridge_flags"]
        ):
            raise RuntimeError(
                f"host-specific Zig build entered portable results: {item['variant']}"
            )
        variant_records[item["variant"]] = record

    dependency_check = subprocess.run(
        [
            "cargo",
            "tree",
            "--manifest-path",
            str(workspace / "source" / "rust" / "Cargo.toml"),
            "--locked",
            "--offline",
        ],
        cwd=workspace,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if dependency_check.returncode:
        raise RuntimeError("the isolated, offline Rust dependency audit failed")
    dependency = {
        "command": [
            "cargo",
            "tree",
            "--manifest-path",
            "source/rust/Cargo.toml",
            "--locked",
            "--offline",
        ],
        "returncode": dependency_check.returncode,
        "stdout": dependency_check.stdout,
        "stderr": dependency_check.stderr,
        "external_packages": max(
            0,
            len([line for line in dependency_check.stdout.splitlines() if line.strip()])
            - 1,
        ),
    }
    if dependency["external_packages"]:
        raise RuntimeError("the isolated Rust build acquired an external package")

    destination.mkdir(parents=True, exist_ok=True)
    bundle = destination / "rust-v6-build-lab.json.gz"
    with bundle.open("wb") as compressed:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=compressed,
            compresslevel=9,
            mtime=0,
        ) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="\n") as stream:
                first = True

                def field(name: str, value: object) -> None:
                    nonlocal first
                    if not first:
                        stream.write(",")
                    first = False
                    stream.write(json.dumps(name))
                    stream.write(":")
                    json.dump(
                        value,
                        stream,
                        sort_keys=True,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )

                def rows(name: str, path: Path) -> None:
                    nonlocal first
                    if not first:
                        stream.write(",")
                    first = False
                    stream.write(json.dumps(name))
                    stream.write(":[")
                    initial = True
                    with path.open(encoding="utf-8") as inputs:
                        for line in inputs:
                            if not initial:
                                stream.write(",")
                            initial = False
                            json.dump(
                                json.loads(line),
                                stream,
                                sort_keys=True,
                                ensure_ascii=False,
                                separators=(",", ":"),
                            )
                    stream.write("]")

                stream.write("{")
                field("schema", "rebar-rust-build-lab-v1")
                field("final_paired_summary", final)
                field("build_variants", variant_records)
                if rejected_threshold_summary is not None:
                    field(
                        "rejected_regression_threshold_summary",
                        rejected_threshold_summary,
                    )
                if finalist is not None:
                    field("finalist_patched_summary", finalist)
                    field("finalist_patched_build_variants", finalist_records)
                field("external_dependency_audit", dependency)
                field(
                    "rejected_unpaired_pilots",
                    [
                        {
                            "label": item["label"],
                            "reason": item["reason"],
                            "summary": item["summary"],
                        }
                        for item in rejected
                    ],
                )
                field("cross_language_experiments", cross)
                field(
                    "cross_language_paired_results",
                    [
                        {
                            "label": item["label"],
                            "summary": item["summary"],
                            "qualification": item["qualification"],
                            "qualification_issues": item["qualification_issues"],
                            "previous_threshold_summary": item[
                                "previous_threshold_summary"
                            ],
                        }
                        for item in cross_paired
                    ],
                )
                field("profile_guided_experiments", profiles)
                rows("final_paired_raw", raw_path)
                if finalist_raw_path is not None:
                    rows("finalist_patched_raw", finalist_raw_path)
                for item in rejected:
                    rows("rejected_unpaired_raw_" + item["label"], item["raw_path"])
                for item in cross_paired:
                    rows("cross_language_paired_raw_" + item["label"], item["raw_path"])
                stream.write("}\n")

    variants = final["variants"]
    strongest = [
        item
        for item in variants
        if item["variant"] != "baseline" and item["portable"] and item["ci95_low"] > 1.0
    ]
    if strongest:
        winner = max(strongest, key=lambda item: item["speedup_vs_current_build"])
        decision = (
            f"The strongest portable practice-only build is `{winner['variant']}` "
            f"at {winner['speedup_vs_current_build']:.4f}× "
            f"(95% interval {winner['ci95_low']:.4f}–{winner['ci95_high']:.4f}×). "
        )
        if winner["regression_cases"]:
            detail = winner["regression_cases"][0]
            decision += (
                f"It has {winner['regressions_gt_20pct']} "
                f"practice slowdown{'s' if winner['regressions_gt_20pct'] != 1 else ''} "
                "above 20%; "
                f"`{detail['api']}` on `{detail['case']}` "
                f"is {(detail['slowdown'] - 1.0) * 100:.2f}% slower. "
            )
        regression_free = [
            item for item in strongest if item["regressions_gt_20pct"] == 0
        ]
        if regression_free:
            safer = max(
                regression_free,
                key=lambda item: item["speedup_vs_current_build"],
            )
            if safer["variant"] != winner["variant"]:
                decision += (
                    "The fastest portable build with no slowdown above 20% "
                    f"is `{safer['variant']}` at "
                    f"{safer['speedup_vs_current_build']:.4f}× "
                    f"(95% interval {safer['ci95_low']:.4f}–"
                    f"{safer['ci95_high']:.4f}×). "
                )
        decision += (
            "These are practice-only results; they do not measure the holdout "
            "or authorize a production build change."
        )
    else:
        decision = (
            "No portable compiler, linker, CPU, or boundary setting has a "
            "confidence interval entirely above the current release build. "
            "Keep the portable production settings unchanged."
        )
    rows_count = final["rows"]
    attempted_count = final.get("attempted_variants", len(variants))
    rejected_builds = final.get("build_failures", [])
    categories_count = len(
        next(item for item in variants if item["variant"] == "baseline")["categories"]
    )
    practice_count = next(item for item in variants if item["variant"] == "baseline")[
        "cases"
    ]
    operation_limit = final.get("maximum_operations_per_case", "NOT MEASURED")
    warmups = final.get("warmups", "NOT MEASURED")
    sample_count = final.get("samples_per_category", 2)
    batch_limit = final.get("maximum_workers_per_batch", 6)
    report = [
        "# Rust build and Python-boundary lab",
        "",
        "This lab tests ways to build the from-scratch Rust regex engine and its "
        "Python extension. It never wraps an outside regex package, never "
        "delegates to Python `re`, and never uses unseen holdout cases to choose "
        "compiler settings.",
        "",
        "## Result",
        "",
        decision,
        "",
        f"The experiment attempts **{attempted_count} builds**; "
        f"**{len(variants)} pass the import and correctness gates**. "
        "The accepted comparison covers "
        f"**{practice_count} frozen practice cases** across "
        f"**{categories_count} categories**, "
        f"**{final['trials']} paired trials**, **{rows_count:,} raw timings**, "
        f"and **{rows_count * 2:,} result checks**. Each build runs in its own "
        "Python process; alternatives are randomly interleaved for every "
        "individual case and trial. Intervals resample both cases and trials.",
        "",
        f"Each pilot uses at most **{operation_limit} operations** per timing "
        f"and **{warmups} untimed warmups**. These caps are for choosing "
        "builds; the separately frozen project holdout keeps its original "
        "operation counts.",
        "",
        "This is a build-selection experiment, not the project's full holdout "
        "score. All results below compare with the existing portable Rust "
        "release build: **1× means the same speed; higher is faster**.",
        "",
        "The case counts use the same frozen practice cases for every build. "
        "A large slowdown means the case took more than 20% longer than "
        "the current Rust build. The baseline has no faster-case count "
        "because it is being compared with itself. Every large slowdown "
        "is individually identified in the evidence bundle by workload, "
        "Python operation, measured speed, and slowdown.",
        "",
        "| Build | Speed | 95% interval | Faster cases | "
        "Large slowdowns | Portable | Extension size |",
        "| --- | ---: | ---: | ---: | ---: | :---: | ---: |",
    ]
    for item in variants:
        faster_cases = (
            "—"
            if item["variant"] == "baseline"
            else f"{item['faster_cases']}/{item['cases']}"
        )
        report.append(
            f"| `{item['variant']}` | "
            f"{item['speedup_vs_current_build']:.4f}× | "
            f"{item['ci95_low']:.4f}–{item['ci95_high']:.4f}× | "
            f"{faster_cases} | {item['regressions_gt_20pct']} | "
            f"{'yes' if item['portable'] else 'no'} | "
            f"{item['bridge_bytes']:,} B |"
        )
    if rejected_builds:
        report.extend(("", "Builds rejected before timing:"))
        for failure in rejected_builds:
            reason = failure.get("error", failure.get("error_type", "build failed"))
            try:
                details = json.loads(reason)
            except (TypeError, ValueError):
                details = {}
            stderr = details.get("stderr", reason)
            first_line = next(
                (line.strip() for line in str(stderr).splitlines() if line.strip()),
                "build or import failed",
            )
            report.append(f"- `{failure['variant']}`: {first_line}")
    if correction is not None:
        report.extend(
            (
                "",
                "An earlier report incorrectly flagged a 20% slowdown only "
                "once it exceeded 25%. Every original timing was audited again "
                "with the correct `speedup < 1 / 1.2` boundary. The unchanged "
                "raw measurements, corrected counts, and original rejected "
                "summary are all preserved in the evidence bundle.",
            )
        )
    if finalist is not None:
        initial_source = final["source_snapshot"]["snapshot_sha256"]
        patched_source = finalist["source_snapshot"]["snapshot_sha256"]
        report.extend(
            (
                "",
                "## Recheck after engine changes",
                "",
                "The broad build screen and the later finalist comparison "
                "use separately recorded source snapshots. The later comparison "
                "rechecks only the leading portable builds after the engine "
                "changed. It uses the same frozen practice-case answers, "
                "randomly interleaves each case and trial, and never reads "
                "the held-out performance test.",
                "",
                f"Original engine SHA-256: `{initial_source['rust/src/lib.rs']}`.",
                f"Rechecked engine SHA-256: `{patched_source['rust/src/lib.rs']}`.",
                "",
                f"The recheck attempts **{finalist['attempted_variants']} builds**; "
                f"**{finalist['correctness_qualified_variants']} pass**. "
                f"It records **{finalist['cases_per_variant']} practice cases**, "
                f"**{finalist['trials']} paired trials**, "
                f"**{finalist['rows']:,} raw timings**, and "
                f"**{finalist['rows'] * 2:,} result checks**.",
                "",
                "| Finalist | Speed | 95% interval | Faster cases | "
                "Large slowdowns | Portable |",
                "| --- | ---: | ---: | ---: | ---: | :---: |",
            )
        )
        for item in finalist["variants"]:
            faster_cases = (
                "—"
                if item["variant"] == "baseline"
                else f"{item['faster_cases']}/{item['cases']}"
            )
            report.append(
                f"| `{item['variant']}` | "
                f"{item['speedup_vs_current_build']:.4f}× | "
                f"{item['ci95_low']:.4f}–{item['ci95_high']:.4f}× | "
                f"{faster_cases} | {item['regressions_gt_20pct']} | "
                f"{'yes' if item['portable'] else 'no'} |"
            )
        if finalist.get("build_failures"):
            report.extend(("", "Finalist builds rejected before timing:"))
            for failure in finalist["build_failures"]:
                report.append(
                    f"- `{failure['variant']}`: "
                    f"{failure.get('error_type', 'build failed')}"
                )
    report.extend(
        (
            "",
            "CPU-specific `native` and `x86-64-v2/v3` builds are explicitly "
            "marked nonportable: they must not become the default for a "
            "drop-in Python replacement. Zig's C compiler also selects the host "
            "CPU by default; a Zig result is marked portable only when explicitly "
            "compiled with `-mcpu=baseline`.",
            "",
            "## Experiments kept, including rejections",
            "",
            "- Early time-separated build runs are preserved in full. They "
            "produced contradictory apparent winners because changing machine "
            "load affected whole variant blocks. Their case-only confidence "
            "intervals did not capture that drift; their rankings are rejected.",
            "- Direct Rust-to-extension static linking, hidden exports, "
            "section-level dead-code removal, and symbol stripping are measured "
            "and their exact binary sizes are included above.",
            "- GCC, Clang, and Zig's C compiler are separately tested. True "
            "cross-language link-time optimization is recorded as rejected "
            "when Rust's LLVM 22 bitcode cannot be read by Zig's LLVM 21.",
            "- Zig's default host-specific machine code and an initially "
            "unloadable static extension are retained as failed experiments. "
            "Only explicit baseline CPU selection, correct unwind linkage, "
            "and a passing real Python import qualify a Zig-built variant.",
            "- Profile-guided Rust builds were actually generated and trained "
            "against the frozen practice suite. LLVM 18 cannot merge Rust's "
            "LLVM 22 raw profile, and a separately recorded header-conversion "
            "experiment proves the profile layouts are incompatible.",
            "- An offline dependency-tree check confirms the engine has "
            "zero outside packages.",
            "",
            "## Reproduce",
            "",
            "```sh",
            "PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
            'PYTHONPATH=. "$PY" tools/rust_build_probe.py list',
            'PYTHONPATH=. "$PY" tools/rust_build_probe.py paired '
            "--workspace /tmp/rebar-rust-build-reproduction "
            f"--samples-per-category {sample_count} "
            f"--max-ops {operation_limit if isinstance(operation_limit, int) else 24} "
            f"--trials {final['trials']} --bootstraps {final['bootstraps']} "
            f"--batch-size {batch_limit}",
        )
    )
    if finalist is not None:
        finalist_names = " ".join(item["variant"] for item in finalist["variants"])
        report.extend(
            (
                "",
                'PYTHONPATH=. "$PY" tools/rust_build_probe.py paired '
                "--workspace /tmp/rebar-rust-build-finalist-reproduction "
                f"--variants {finalist_names} "
                f"--samples-per-category {finalist['samples_per_category']} "
                f"--max-ops {finalist['maximum_operations_per_case']} "
                f"--trials {finalist['trials']} "
                f"--bootstraps {finalist['bootstraps']} "
                f"--batch-size {finalist['maximum_workers_per_batch']}",
            )
        )
    report.extend(
        (
            "```",
            "",
            "The deterministic, compressed lab includes the complete "
            "measurements, frozen practice-case hashes, build commands, "
            "source hashes, all rejected raw pilots, LLVM diagnostics, "
            "and the original training profile: "
            "[`rust-v6-build-lab.json.gz`](rust-v6-build-lab.json.gz).",
            "",
            f"Bundle SHA-256: `{file_hash(bundle)}`.",
        )
    )
    report_path = destination / "RUST-V6-BUILD-LAB.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return {
        "schema": "rebar-rust-build-lab-export-v1",
        "report": str(report_path),
        "bundle": str(bundle),
        "bundle_sha256": file_hash(bundle),
        "rows": final["rows"],
        "variants": len(variants),
        "attempted_variants": attempted_count,
        "rejected_builds": len(rejected_builds),
        "rejected_unpaired_pilots": len(rejected),
        "cross_experiments": len(cross),
        "cross_paired_experiments": len(cross_paired),
        "external_packages": dependency["external_packages"],
        "regression_speedup_threshold": correct_threshold,
        "reported_large_slowdowns": sum(
            item["regressions_gt_20pct"] for item in variants
        ),
        "reclassified_variants": (
            correction["changed_variants"] if correction is not None else 0
        ),
        "finalist_variants": len(finalist_records),
        "finalist_rows": finalist["rows"] if finalist is not None else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    matrix = commands.add_parser("matrix", help="build and compare isolated variants")
    matrix.add_argument("--workspace", type=Path)
    matrix.add_argument(
        "--source-ref",
        help="snapshot a committed revision instead of in-progress working files",
    )
    matrix.add_argument("--variants", nargs="+")
    matrix.add_argument("--samples-per-category", type=int, default=2)
    matrix.add_argument("--max-ops", type=int, default=24)
    matrix.add_argument("--trials", type=int, default=5)
    matrix.add_argument("--bootstraps", type=int, default=1000)

    build = commands.add_parser("build", help="only build isolated variants")
    build.add_argument("--workspace", type=Path, required=True)
    build.add_argument(
        "--source-ref",
        help="snapshot a committed revision instead of in-progress working files",
    )
    build.add_argument("--variants", nargs="+")

    measure = commands.add_parser("measure", help="measure existing isolated variants")
    measure.add_argument("--workspace", type=Path, required=True)
    measure.add_argument("--variants", nargs="+")
    measure.add_argument("--samples-per-category", type=int, default=2)
    measure.add_argument("--max-ops", type=int, default=24)
    measure.add_argument("--trials", type=int, default=5)
    measure.add_argument("--bootstraps", type=int, default=1000)

    paired = commands.add_parser(
        "paired",
        help="interleave isolated builds for every frozen practice case and trial",
    )
    paired.add_argument("--workspace", type=Path, required=True)
    paired.add_argument(
        "--source-ref",
        help="snapshot a committed revision when creating a new workspace",
    )
    paired.add_argument("--variants", nargs="+")
    paired.add_argument("--samples-per-category", type=int, default=2)
    paired.add_argument("--max-ops", type=int, default=24)
    paired.add_argument("--trials", type=int, default=7)
    paired.add_argument("--bootstraps", type=int, default=2000)
    paired.add_argument("--batch-size", type=int, default=6)

    train = commands.add_parser(
        "train", help="train an isolated instrumented Rust build"
    )
    train.add_argument("--workspace", type=Path, required=True)
    train.add_argument("--variant", default="rust-pgo-generate")
    train.add_argument("--samples-per-category", type=int, default=2)
    train.add_argument("--max-ops", type=int, default=12)
    train.add_argument("--passes", type=int, default=2)

    compatibility = commands.add_parser(
        "profile-header-experiment",
        help="record an explicitly experimental LLVM raw-profile compatibility test",
    )
    compatibility.add_argument("--input", type=Path, required=True)
    compatibility.add_argument("--output", type=Path, required=True)

    profile_merge = commands.add_parser(
        "merge-profile",
        help="preserve the exact result of an LLVM profile-merge experiment",
    )
    profile_merge.add_argument("--workspace", type=Path, required=True)
    profile_merge.add_argument("--input", type=Path, required=True)
    profile_merge.add_argument("--output", type=Path, required=True)
    profile_merge.add_argument("--tool", default="llvm-profdata-18")
    profile_merge.add_argument("--label", required=True)

    export = commands.add_parser(
        "export-lab",
        help="write the reproducible Rust build report and deterministic evidence bundle",
    )
    export.add_argument("--workspace", type=Path, required=True)
    export.add_argument(
        "--destination",
        type=Path,
        default=ROOT / "candidates" / "evidence",
    )
    export.add_argument("--unpaired-workspace", type=Path, action="append", default=[])
    export.add_argument("--cross-workspace", type=Path, action="append", default=[])
    export.add_argument("--profile-workspace", type=Path)
    export.add_argument("--finalist-workspace", type=Path)

    reclassify = commands.add_parser(
        "reclassify-regressions",
        help="correct 20%% slowdown labels from original paired rows without retiming",
    )
    reclassify.add_argument("--workspace", type=Path, required=True)

    commands.add_parser(
        "threshold-self-test",
        help="prove that every slowdown above 20%% is reported",
    )

    child = commands.add_parser("worker", help=argparse.SUPPRESS)
    child.add_argument("--package-root", type=Path, required=True)
    child.add_argument("--variant", required=True)
    child.add_argument("--trial", type=int, required=True)
    child.add_argument("--samples-per-category", type=int, required=True)
    child.add_argument("--max-ops", type=int, required=True)

    streaming_child = commands.add_parser("stream-worker", help=argparse.SUPPRESS)
    streaming_child.add_argument("--package-root", type=Path, required=True)
    streaming_child.add_argument("--variant", required=True)
    streaming_child.add_argument("--samples-per-category", type=int, required=True)

    show = commands.add_parser("list", help="list build variants")
    show.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "list":
        if args.json:
            print(json.dumps([asdict(item) for item in VARIANTS], sort_keys=True))
        else:
            for variant in VARIANTS:
                print(variant.name)
        return
    if args.command == "threshold-self-test":
        print(json.dumps(regression_threshold_self_test(), sort_keys=True))
        return
    if args.command == "reclassify-regressions":
        print(
            json.dumps(
                reclassify_paired_regressions(args.workspace.resolve()), sort_keys=True
            )
        )
        return
    if args.command == "worker":
        if args.max_ops <= 0 or args.samples_per_category <= 0:
            raise SystemExit("operation and sample counts must be positive")
        worker(args)
        return
    if args.command == "stream-worker":
        if args.samples_per_category <= 0:
            raise SystemExit("the sample count must be positive")
        stream_worker(args)
        return
    if args.command == "train":
        if args.passes <= 0 or args.samples_per_category <= 0 or args.max_ops <= 0:
            raise SystemExit("pass, sample, and operation counts must be positive")
        result = train_profile(
            args.workspace.resolve(),
            args.variant,
            args.samples_per_category,
            args.max_ops,
            args.passes,
        )
        print(json.dumps(result, sort_keys=True))
        return
    if args.command == "profile-header-experiment":
        result = profile_header_experiment(args.input.resolve(), args.output.resolve())
        print(json.dumps(result, sort_keys=True))
        return
    if args.command == "merge-profile":
        result = merge_profile(
            args.workspace.resolve(),
            args.input.resolve(),
            args.output.resolve(),
            args.tool,
            args.label,
        )
        print(json.dumps(result, sort_keys=True))
        if result["returncode"]:
            raise SystemExit(result["returncode"])
        return
    if args.command == "export-lab":
        result = export_lab(
            args.workspace.resolve(),
            args.destination.resolve(),
            [path.resolve() for path in args.unpaired_workspace],
            [path.resolve() for path in args.cross_workspace],
            args.profile_workspace.resolve() if args.profile_workspace else None,
            args.finalist_workspace.resolve() if args.finalist_workspace else None,
        )
        print(json.dumps(result, sort_keys=True))
        return
    if args.command == "paired":
        if (
            args.trials <= 0
            or args.samples_per_category <= 0
            or args.max_ops <= 0
            or args.batch_size < 2
        ):
            raise SystemExit(
                "trial, sample, operation, and paired-batch counts are invalid"
            )
        if args.bootstraps < 40:
            raise SystemExit("at least 40 deterministic bootstrap samples are required")
        workspace = args.workspace.resolve()
        if not (workspace / "source-manifest.json").is_file():
            prepare(workspace, args.source_ref)
        elif args.source_ref is not None:
            prepare(workspace, args.source_ref)
        wanted = choose_variants(args.variants)
        variants = []
        failed = []
        for variant in wanted:
            metadata = workspace / "variants" / variant.name / "build.json"
            if not metadata.is_file():
                try:
                    build_variant(workspace, variant)
                except Exception as error:
                    failure = {
                        "variant": variant.name,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                    failed.append(failure)
                    print(json.dumps(failure, sort_keys=True), flush=True)
                    continue
            variants.append(variant)
        if failed:
            (workspace / "paired-build-failures.json").write_text(
                json.dumps(failed, sort_keys=True, indent=2) + "\n"
            )
        if not any(item.name == "baseline" for item in variants):
            raise SystemExit("the isolated baseline Rust build failed")
        raw = paired_trials(
            workspace,
            variants,
            args.trials,
            args.samples_per_category,
            args.max_ops,
            args.batch_size,
        )
        summary = summarize_paired(
            workspace,
            args.trials,
            args.samples_per_category,
            args.bootstraps,
            args.max_ops,
            args.batch_size,
            len(wanted),
            failed,
        )
        print(
            json.dumps(
                {
                    "workspace": str(workspace),
                    "raw": str(raw),
                    "rows": summary["rows"],
                    "pairing": summary["pairing"],
                    "rankings": [
                        {
                            "variant": row["variant"],
                            "speedup": row["speedup_vs_current_build"],
                            "ci95": [row["ci95_low"], row["ci95_high"]],
                            "portable": row["portable"],
                            "static_bridge": row["static_bridge"],
                        }
                        for row in summary["variants"]
                    ],
                },
                sort_keys=True,
            )
        )
        return

    workspace = (
        args.workspace.resolve()
        if args.workspace is not None
        else Path(tempfile.mkdtemp(prefix="rebar-rust-build-")).resolve()
    )
    variants = choose_variants(args.variants)
    if args.command in {"build", "matrix"}:
        prepare(workspace, args.source_ref)
        successful = []
        failed = []
        for variant in variants:
            try:
                record = build_variant(workspace, variant)
            except Exception as error:
                failure = {
                    "variant": variant.name,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
                failed.append(failure)
                print(json.dumps(failure, sort_keys=True), flush=True)
            else:
                successful.append(variant)
                print(
                    json.dumps(
                        {
                            "variant": variant.name,
                            "engine_bytes": record["engine_bytes"],
                            "bridge_bytes": record["bridge_bytes"],
                            "portable": variant.portable,
                            "static_bridge": variant.static_bridge,
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
        (workspace / "build-failures.json").write_text(
            json.dumps(failed, sort_keys=True, indent=2) + "\n"
        )
        if not any(variant.name == "baseline" for variant in successful):
            raise SystemExit("the baseline Rust build failed")
        variants = successful
        if args.command == "build":
            print(json.dumps({"workspace": str(workspace), "failed": len(failed)}))
            return
    if args.trials <= 0 or args.samples_per_category <= 0 or args.max_ops <= 0:
        raise SystemExit("trial, sample, and operation counts must be positive")
    if args.bootstraps < 40:
        raise SystemExit("at least 40 deterministic bootstrap samples are required")
    raw = run_trials(
        workspace,
        variants,
        args.trials,
        args.samples_per_category,
        args.max_ops,
    )
    summary = summarize(workspace, args.trials, args.bootstraps)
    print(
        json.dumps(
            {
                "workspace": str(workspace),
                "raw": str(raw),
                "rows": summary["rows"],
                "rankings": [
                    {
                        "variant": row["variant"],
                        "speedup": row["speedup_vs_current_build"],
                        "ci95": [row["ci95_low"], row["ci95_high"]],
                        "portable": row["portable"],
                        "static_bridge": row["static_bridge"],
                    }
                    for row in summary["variants"]
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
