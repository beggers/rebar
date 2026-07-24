# From-scratch language and Python boundary landscape

Status: **SOURCE-ONLY. NOT A CORRECTNESS REPORT. NO PERFORMANCE OR HOLDOUT RESULTS.**

The goal is a complete, faster, independently implemented replacement for
Python's `re`, not a wrapper around an existing matching package. This snapshot
records what source and compilers actually exist. It does not claim that any
engine builds, passes the complete frozen oracle, is safe, or is faster.

## Five independently authored source paths

The immutable V9 `FAMILIES` declaration registers exactly **three** current
families: Rust, C, and Zig. C++ and Go are separately authored, source-only
experiments; they are **not registered or qualified candidates**.

| Language | Matching implementation written in this project | Python boundary | Status |
| --- | --- | --- | --- |
| Rust | Its own expression parser, instructions, compiler, backtracking stack, search, and Unicode tables in `candidates/rust/src/`. | Owned C extension and explicit Rust C-callable interface. | Registered family; full qualification **NOT ESTABLISHED HERE**. |
| C | Its own Python frame-stack parser and compiler in `candidates/vm_candidate.py`, with separate owned instructions and execution in `candidates/_vm_native.c`. | Direct CPython C extension. | Registered family; full qualification **NOT ESTABLISHED HERE**. |
| Zig | Its own parser, expression nodes, instructions, compiler, and executor in `candidates/zig/mini_regex.zig`. | Owned C-callable Zig engine, direct CPython bridge, and `ctypes` loader. | Registered family; full qualification **NOT ESTABLISHED HERE**. |
| C++ | Its own parser, instruction representation, compiler, and backtracking machine in `experiments/cpp_from_scratch_v1/engine.hpp` and `engine.cpp`. | Separately authored direct CPython bridge in `py_bridge.cpp`. | Source-only experiment; **NOT BUILT. NOT RUN. NOT QUALIFIED.** |
| Go | Its own lexer, parser, expression compiler, and continuation-based executor in `experiments/go_from_scratch_v1/engine.go`; `go.mod` declares no external dependencies. | Owned versioned C interface in `exports.go` and separately authored CPython bridge in `python_bridge.c`. | Source-only experiment; **NOT BUILT. NOT RUN. NOT QUALIFIED.** |

An independent family must own its actual semantic parser, compiler, and
matching executor. Changing a binding, compiler setting, wrapper, calling
convention, or loader around the same engine does **not** create a sixth family.
Neither the standard-library matcher, `_sre`, another candidate, nor an
external regular-expression package may perform production matching.

## Compiler availability actually observed

Each entry was checked with a separate `command -v`; no compiler was run,
except the exact locked Zig binary's `version` command.

| Tool | Actual local observation |
| --- | --- |
| C | `cc`: `/usr/bin/cc`. |
| C++ | `c++`: `/usr/bin/c++`. |
| Rust | `rustc`: `/home/dev-user/.cargo/bin/rustc`; `cargo`: `/home/dev-user/.cargo/bin/cargo`. |
| Go | `go`: `/home/dev-user/.openai/bin/go`. |
| Zig | Exact pinned executable reports `0.16.0`; its SHA-256 matches the official-toolchain lock. |
| Java | Runtime `/usr/bin/java` exists; `javac` is **NOT AVAILABLE** on `PATH`. A Java compiler was not observed. |
| Nim, Swift, .NET, WebAssembly | `nim`, `swift`, `dotnet`, and `wasmtime` are **NOT AVAILABLE** on `PATH`. |

The Zig source is the project's own `candidates/zig/mini_regex.zig`, not a
third-party matching package. The exact compiler is
`/tmp/rebar-zig-0.16.0.pTlEyN4d/zig-x86_64-linux-0.16.0/zig`.
Its measured SHA-256 is
`2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c`,
exactly the `compiler_sha256` in `toolchains/zig-0.16.0.lock.json`.
The lock additionally records archive SHA-256
`70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00`;
the archive itself was **NOT RECHECKED** for this source-only snapshot.

## Python-boundary experiments, not speed claims

Direct CPython extensions can construct native Python pattern and match
objects without first copying every input. A small explicit C-callable
interface can connect an independently owned Rust, Zig, Go, or C++ engine
to such an extension. `ctypes`, CFFI, and a Rust binding helper such as PyO3
are alternative ways to cross that boundary; they count only as bindings,
never as matching engines or additional candidate families. Their package
availability, safety, buildability, compatibility, copying costs, callback
costs, memory use, and relative speed are **NOT MEASURED**.

Go additionally requires explicit runtime, handle, pointer, and callback
ownership. Java, Nim, Swift, .NET, and WebAssembly are future hypotheses,
not runnable independently authored families established by this snapshot.
Any new implementation must first freeze its own source, demonstrate
non-delegation, and pass the unchanged complete correctness oracle before
any benchmark or holdout is permitted.

**Qualified winner: NONE. Speed, confidence, memory, regression rates,
rankings, and expanded-holdout results: NOT MEASURED.**
