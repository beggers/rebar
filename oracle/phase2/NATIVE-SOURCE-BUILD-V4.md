# Six independently built regular-expression engines

This is a source and build freeze, not a test result. Its purpose is to make
sure that six proposed Python `re` replacements are built from their own
source code, not wrappers around an existing regular-expression engine.

Freeze, commit, and push this protocol, the exact
[`native-source-build-v4.json`](native-source-build-v4.json), and the
standalone
[`../../tools/reproduce_owned_native_source_build_v4.py`](../../tools/reproduce_owned_native_source_build_v4.py)
before authorizing any version-four build. The recorder has two safe,
separately named source-only operations. Neither operation starts a compiler,
imports a candidate, measures time, opens a performance benchmark, or reads a
hidden holdout.

## The unchanged correctness standard

The baseline is the exact pinned stable CPython **3.14.6**. Its frozen
correctness oracle has **13 suites and 31,237 case executions**. The exact
manifest is
[`../phase1/p0-completeness-v1.json`](../phase1/p0-completeness-v1.json),
SHA-256
`cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`.

The count is of independently frozen suite executions, not a claim that all
patterns are globally unique. All 13 reference results passed; this does not
mean any candidate has passed them. The original hidden holdout remains
closed. Enlarging a future held-out performance test requires its own frozen,
committed, and pushed phase-three protocol; no cases or results from that test
are accessed here.

## Six independent families, not six wrappers

| Language | Owned matching implementation | Separate Python entry point |
| --- | --- | --- |
| C | `candidates/_vm_native.c` | `candidates/vm_candidate.py` |
| Rust | The seven owned Rust and Cargo source files plus `candidates/rust/py_bridge.c` | `candidates/rust_candidate.py` |
| Zig | `candidates/zig/mini_regex.zig` and `candidates/zig/py_bridge.c` | `candidates/zig_candidate.py` |
| C++ | `candidates/cpp/engine.hpp`, `engine.cpp`, and `py_bridge.cpp` | `candidates/cpp_candidate.py` |
| Go | `candidates/go/go.mod`, `engine.go`, and `py_bridge.c` | `candidates/go_candidate.py` |
| Fortran | `candidates/fortran/engine.f90` and `py_bridge.c` | `candidates/fortran_candidate.py` |

The machine-readable contract fixes the exact **25** source paths, SHA-256
hashes, and byte counts. A file may belong to exactly one family. Omitting the
C++ header, a Rust module, the Go module, a Python entry point, or any bridge
fails the freeze. Adding a previously built library, another candidate,
Python `re`, `_sre`, Rust crates, a Go dependency, Go `regexp`, Go
`regexp/syntax`, C++ `<regex>`, `std::regex`, Boost.Regex, RE2, PCRE,
Oniguruma, Hyperscan, a network fetch, a subprocess-based matcher, or a
fallback also fails.

The two old static-independence documents cover their original families only.
They are retained and authenticated, not described as having already
certified C++, Go, or Fortran.

## Honest, pinned toolchains

The contract identifies exact compiler binaries and full-file hashes. It fixes
CPython 3.14.6 and its actual headers, host GCC/G++/GNU Fortran 13, the real
resolved Go 1.26.3 executable, Rust/Cargo 1.95.0 and the matching compiler
driver, GNU `readelf`, and the official stable Zig 0.16.0 release archive,
release lock, and actual compiler. The official Zig compiler is at
`/tmp/zig-x86_64-linux-0.16.0/zig`. It is not required to be on `PATH`; an
empty `PATH` lookup is not evidence that the pinned compiler is missing. The
recorder verifies file bytes without running a version command in either safe
source-only mode. A missing or changed exact compiler is reported as a
blocker, never replaced with a different compiler.

Rust builds must use the exact dependency-free, first-party `Cargo.toml` and
`Cargo.lock`, `--locked --offline --frozen`, a phase-owned Cargo home and
target, and the directly pinned Rust compiler. Go builds must use the exact
single first-party `go.mod`, `GOPROXY=off`, `GOSUMDB=off`, `GOWORK=off`,
`GOENV=off`, `GOTOOLCHAIN=local`, separate fresh module/build caches, the
pinned C compiler, and `-buildmode=c-shared`. No language package or regular
expression is downloaded or supplied by a third party.

## The generated Go boundary is real build output

The existing Go C bridge declares its owned entry points by hand; this is not
proof that those declarations match the Go compiler's application binary
interface. Each actual future Go phase must create its own fresh
`_go_engine.so` **and the matching compiler-generated `_go_engine.h`** in its
private native-output directory. The recorder authenticates the complete
header, checks all nine `rebar_go_*` exports, and passes that exact file to the
bridge compiler with `-include`. A missing, reused, pre-existing, foreign,
edited, non-reproducible, or application-binary-interface-inconsistent header
fails the build. The two generated headers must be byte-identical but have
distinct private paths and inodes.

Go uses process-global `runtime/cgo` handles and `sync.Once`/atomic state.
Source ownership does **not** establish safety in multiple Python
subinterpreters. The separately frozen full correctness gate must run the
actual subinterpreter suite; its status here is **NOT MEASURED**.

The C++ and Go bridges may import exactly Python `unicodedata` as ordinary
Unicode support. The Rust bridge retains its separately documented literal
`copyreg`, `functools`, and `inspect` support imports. None authorizes
`re`, `_sre`, computed imports, another candidate, or an existing matcher.
Actual transitive runtime non-delegation remains a later trapped correctness
gate; static inspection alone is not described as proving it.

## Two fresh builds and complete native evidence

An actual build is allowed only after this three-file freeze has been
published and its exact recorder, protocol, contract, and every owned source
have been independently pinned on the command line. Each family then builds
twice under a new mode-`0700` root matching
`/tmp/rebar-phase2-native-build-v4-FAMILY-`. The phase names are
`reference-a` and `reference-b`. Source copies, source inodes, native
outputs, output inodes, temporary directories, module outputs, Rust targets,
Go caches, Zig caches, compiler processes, and working directories must all be
distinct. Every matching native output, including the generated Go header,
must have exactly equal bytes and the same SHA-256 in both phases. A failed
build or unequal output is retained as a failure; it never becomes a passing
result.

The recorder retains full exact argument vectors, private working directories,
restricted environments, unique positive process identifiers, exit codes, and
complete SHA-256-checked standard-output and standard-error streams.
`readelf` authenticates complete dynamic library dependencies, all dynamic
symbol rows, versioned undefined symbols, owned entry points, and the exact
adjacent-library search path `$ORIGIN`. `RPATH`, foreign engines, sibling
engines, incomplete symbol tables, and arbitrary library search paths fail.
Runtime-library allowlists are family-specific: C++ may use its own
`libstdc++.so.6`; Fortran may use its own `libgfortran.so.5` and
`libquadmath.so.0`. These permissions do not extend to another family.

Zig retains the exact official compiler-native `-fstrip` correction, separate
phase-owned local and global caches, and the authentic old failure. Stripping
an already generated file, sharing a cache, omitting the compiler flag, or
silently reclassifying the previous result is forbidden.

Future reports use only version-four schema and the exclusively created,
canonical, bounded, synchronized evidence names:

```text
native-source-build-v4-FAMILY-LABEL.json.gz
native-source-build-v4-FAMILY-LABEL-publication-receipt.json
native-source-build-v4-FAMILY-LABEL-failures.json.gz
native-source-build-v4-FAMILY-LABEL-failures-publication-receipt.json
```

An old V2/V3 activator does not accept version-four evidence. Never relabel a
V4 result as V2/V3, change an existing consumer, activate a V4 library, or
qualify a candidate until a separately frozen, committed, and pushed V4
activation and complete candidate correctness gate exists.

## Keep the actual earlier failures

The full V2 source and protocol and V3 source and protocol remain unchanged.
V2 recorded reproducible C and Rust builds and an authentic Zig
reproducibility **failure**. Both Zig engine files were 480,040 bytes but
had different hashes because debug sections contained their distinct private
source and cache paths. The bridge bytes matched. All 15 recorded Zig
compiler/inspection processes succeeded. This was not a missing Zig
compiler, a GNU build-ID difference, a failed bridge, or a candidate
correctness failure.

The V4 contract independently pins and verifies all six exact V2 archives
and publication receipts, including the Zig failure, all recorded process
streams, the original phase outputs, the independently falsified historical
V1 symbol audit, and exact old recorder/protocol hashes. A durable receipt
for a failed build proves only that its **FAIL** was safely preserved.

## Reproduce the safe source-only checks

Run the complete synthetic, in-memory positive and hostile controls normally
and in an empty environment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v4.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v4.py --self-test
```

`--self-test` is guarded against all real file operations, subprocesses,
temporary directories, threads, clocks, network connections, candidate
imports, and native library loads. Its actual-effect counters must all be
zero. Its full output must be identical in both environments.

After that, separately read and authenticate only the explicitly frozen
source files, exact toolchain bytes, old evidence, and correctness manifest:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v4.py --verify-context

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v4.py --verify-context
```

`--verify-context` is read-only. It does not invoke a compiler or another
process, run a candidate, create a directory, consult the ambient `PATH`,
read a benchmark, or access either final holdout. It reports missing pinned
toolchains as named blockers.

Current V4 build status: **NOT RUN**. Candidates passing all 31,237 cases:
**0**. Go subinterpreter safety, native undefined behavior, execution speed,
memory use, the expanded holdout, and a winner: **NOT MEASURED**.
