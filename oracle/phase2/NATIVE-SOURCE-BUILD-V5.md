# Six original matching engines and the corrected Go build

This is a source and build freeze, not a correctness result or a speed claim.
Its purpose is to ensure that six proposed Python `re` replacements are made
from their own matching source. No candidate may wrap Python `re`, another
candidate, Go `regexp`, C++ `<regex>`, a Rust crate, a Python package, or an
external native regular-expression engine.

Commit and push this document,
[`native-source-build-v5.json`](native-source-build-v5.json), and
[`../../tools/reproduce_owned_native_source_build_v5.py`](../../tools/reproduce_owned_native_source_build_v5.py)
as a focused source-freeze chunk before authorizing any V5 build. The safe
commands below do not authorize a build.

## The standard remains unchanged

The baseline is the pinned stable **CPython 3.14.6**. The published
correctness oracle remains **13 suites and 31,237 case executions**, exactly
as recorded in
[`../phase1/p0-completeness-v1.json`](../phase1/p0-completeness-v1.json),
SHA-256
`cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`.

These are reference case executions, not a count of globally distinct
patterns or evidence that any replacement has passed. Qualified replacement
count: **0**. Replacement correctness, memory, speed, and subinterpreter
safety: **NOT MEASURED**. The hidden performance holdout remains **NOT
OPENED**. Enlarging it requires its own later frozen, committed, and pushed
performance protocol after the correctness gate; this source freeze neither
reads nor creates holdout cases.

## Six original families

| Language | Original owned matching source | Python entry point |
| --- | --- | --- |
| C | `candidates/_vm_native.c` | `candidates/vm_candidate.py` |
| Rust | Seven owned Rust and Cargo sources and `candidates/rust/py_bridge.c` | `candidates/rust_candidate.py` |
| Zig | `candidates/zig/mini_regex.zig` and `candidates/zig/py_bridge.c` | `candidates/zig_candidate.py` |
| C++ | `candidates/cpp/engine.hpp`, `engine.cpp`, and `py_bridge.cpp` | `candidates/cpp_candidate.py` |
| Go | `candidates/go/go.mod`, `engine.go`, and `py_bridge.c` | `candidates/go_candidate.py` |
| Fortran | `candidates/fortran/engine.f90` and `py_bridge.c` | `candidates/fortran_candidate.py` |

The contract pins exactly **25 different source file owners**, including
every Python entry point, header, package file, matching implementation, and
Python bridge. Reusing source across families, importing another candidate,
linking an existing matcher, introducing an external package, or providing a
fallback fails the source gate.

The read-only context also runs the exact, previously published
[`CANDIDATE-INDEPENDENCE-V2.md`](CANDIDATE-INDEPENDENCE-V2.md)
six-family static source audit. Its full first-party source is pinned to
`57168db3df64414a7dc27f1793d9c22b7c493a8b37c025dc57243796e892d93c`
and its complete machine inventory is pinned to
`89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659`.
It checks all six real parsers, compilers, executors, and bridges. It rejects
external matcher packages, active foreign cgo comments, hidden Go linker
directives, and non-first-party Fortran source or bindings. Go must have its
exact one header-only cgo preamble and nine owned exports; Fortran must have
all 12 of its own engine and callback bindings. This static source result is
not runtime non-delegation or candidate correctness.

## Preserve the real failed Go experiment

The V4 Go attempt genuinely failed. Its Go build ran from
`reference-a/source/candidates/go`, where the independently owned
`py_bridge.c` was also present. Go therefore treated the Python C bridge as a
C source belonging to the Go package and its compiler emitted:

```text
# rebar.local/candidates/go
py_bridge.c:2:10: fatal error: Python.h: No such file or directory
    2 | #include <Python.h>
      |          ^~~~~~~~~~
compilation terminated.
```

The exact diagnostic is **175 bytes**, SHA-256
`4173a7583fe0358c92056da596f06837bd7a888aa56d6e66cb2920d806600862`.
There were four real V4 Go processes: the readelf, GCC, and Go version
commands succeeded; `build_go_engine` exited with status `1`. No Go build
phase completed. The authentic V4 report is
[`evidence/native-source-build-v4-go-phase2-v4-failures.json.gz`](evidence/native-source-build-v4-go-phase2-v4-failures.json.gz),
SHA-256
`fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb`.

The associated publication receipt has `status: PASS` because the failure
was safely written; its **`build_status` is `FAIL`**. Publication success is
not build success, candidate qualification, or a performance result.

This is a package-isolation error. It is not evidence of a missing Go
compiler, missing pinned Python headers, a failed matching algorithm, an
external regex dependency, or a candidate correctness result.

## The precise Go correction

Each future V5 Go phase creates its own mode-`0700` directory:

```text
reference-a/go-engine-package/go.mod
reference-a/go-engine-package/engine.go
reference-a/source/candidates/go/py_bridge.c
reference-a/native/_go_engine.so
reference-a/native/_go_engine.h
reference-a/native/_go_bridge.cpython-314-x86_64-linux-gnu.so
```

The `reference-b` paths are independently created and have distinct inodes.
Only the exact frozen, first-party `go.mod` and `engine.go` are independently
copied into `go-engine-package`. Its complete directory listing must be
exactly `engine.go` and `go.mod`. The exact, separately snapshotted Python
bridge stays in the original phase-owned source tree and never becomes a Go
package input.

The exact pinned Go compiler runs `go build -buildmode=c-shared` from the
two-file directory. This creates the actual `_go_engine.so` **and the Go
compiler's actual `_go_engine.h`** in the fresh phase-owned native output
directory. The independent pinned GCC command compiles the separate original
`py_bridge.c` and forcibly includes that exact newly generated header using
`-include`. All nine genuine owned Go matching declarations must be present.
The two phases must produce byte-identical engines, bridges, and generated
headers while retaining distinct source, cache, output, and process owners.

Go remains completely offline: `GOPROXY=off`, `GOSUMDB=off`, `GOWORK=off`,
`GOENV=off`, `GOTOOLCHAIN=local`, fresh separate Go build and module caches,
and the exact pinned GCC. There is one first-party module and **zero external
packages**. A copied C bridge in the Go package, a missing or reused header,
a shared inode, a manually written header, a substitute compiler, a registry
access, or a bridge compiled before header verification fails the build.

## Honest historical accounting

The actual earlier C, Rust, and Zig candidate history has **17 distinct
evidence file owners per family**, or **51** in total. The actual V4 C++
success adds one archive and one receipt. The actual V4 Go failure adds one
failure archive and one receipt. The actual V4 Fortran reproducibility
failure adds another failure archive and receipt. Together these are **57
distinct evidence file owners**, each checked by exact path, complete file
hash, mode `0600`, and a unique device/inode pair.

Evidence files are not compiler processes. The original V2 source-build
history contains **39** real processes: C 8, Rust 16, and the actual failed
Zig reproduction 15. The genuine V4 C++ success has **10** processes; the
genuine V4 Go failure has **4**; and the genuine V4 Fortran failure has
**18**. The total preserved V2 and V4 process count is therefore **71**, not
57. Process identifiers are checked for uniqueness within their actual
recorded run; unrelated historical runs may use the same numerical process
identifier. Earlier Zig, Go, and Fortran failures remain failures. None of
these source builds establishes candidate correctness or speed.

## Preserve the real failed Fortran experiment

The V4 Fortran experiment ran **18 real compiler and native inspection
processes, all of which exited successfully**. It completed both independent
source phases, including both matching engines, both bridges, all nine engine
exports, and all three owned reverse callbacks. It failed only when comparing
the completed engine files:

| Phase | Engine bytes | Engine SHA-256 |
| --- | ---: | --- |
| `reference-a` | 74,624 | `37557a44033a80aa11a81fa145ca76c2bbd44ee544b31974dcf6e59ba0f2949c` |
| `reference-b` | 74,624 | `696126d3f3e7239cac55975f53beb3b5e5cffc6948f08258817b6b2d86422199` |

The independently compiled **37,424-byte bridges were identical**, with
SHA-256
`eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26`.
The precise differing binary section was **NOT RECORDED**. This failure is
not a failed compiler, missing bridge, unbuilt phase, source correctness
failure, or proof of a particular ELF-section cause.

The exact preserved report is
[`evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz`](evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz),
SHA-256
`ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103`.
Its durable receipt has `status: PASS` and **`build_status: FAIL`**.

The V5 Fortran plan freezes one compiler random seed,
`-frandom-seed=rebar-fortran-v5`, and maps both complete private phase roots,
including module-output directories, to one canonical prefix. These options
are a **design hypothesis, not a demonstrated fix**. A later actual two-phase
build must still independently establish byte identity.

Each later V5 native binary also receives its own complete
`readelf --sections --wide` and `readelf --notes --wide` forensic process.
Their complete arguments, working directories, restricted environments,
process identifiers, exit statuses, and full authenticated output are
preserved. Individual binary section payload hashes remain **NOT RECORDED**;
section-listing output is not misrepresented as raw section bytes. These
future process counts are recorded separately from the actual 71 historical
processes.

The actual V4 C++ archive is
[`evidence/native-source-build-v4-cpp-phase2-v4.json.gz`](evidence/native-source-build-v4-cpp-phase2-v4.json.gz),
SHA-256
`48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9`.
The exact published historical candidate graph is
[`../../docs/evidence/candidate-current-overview-v10.inputs.json`](../../docs/evidence/candidate-current-overview-v10.inputs.json),
SHA-256
`bfc68aa4f6c97d9e4571d4cd062cd1cb706d9d50fdd9f1ea6ccb329081037989`.
That genuine V10 snapshot predates the actual Fortran experiment and
correctly says Fortran had not yet been built. The separately authenticated
later Fortran failure is added as its own evidence; the older graph is never
rewritten or claimed to have observed it. The graph retains the actual
earlier semantic mismatch counts: C **2,094**, Rust **2,042**, and Zig
**1,764**. All three remain unqualified.
The V5 recorder verifies the full compressed historical V4 reports, durable
receipts, complete output streams, exact recorded working directories,
offline environments, process identities, unchanged failure classifications,
all 51 candidate evidence owners, and all six V4 evidence owners without
running another process.

## Exact offline toolchain

The machine contract pins the same **13** actual compiler, interpreter,
header, archive, and compiler-driver files as V4, including stable CPython
3.14.6, GCC/G++/GNU Fortran 13, Go 1.26.3, Rust/Cargo 1.95.0, GNU readelf,
and the real official stable Zig 0.16.0 binary and release archive. The
actual Zig binary is `/tmp/zig-x86_64-linux-0.16.0/zig`; absence from an
ambient `PATH` is not a missing compiler. Rust uses its exact first-party
lockfile and offline Cargo flags. Zig retains its actually supported
compiler-native `-fstrip` correction. No registry, network, external regex
library, candidate process, candidate import, native library load, timing,
memory measurement, or benchmark is authorized by either safe command.

## Safe reproduction

Run the synthetic effect-blocked controls in a normal environment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v5.py --self-test
```

Repeat the exact same source-only check in an empty environment:

```text
env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v5.py --self-test
```

Verify the complete pinned context, actual V2 and V4 history, exact three
failed candidate histories, the 57 evidence file owners, the 71 historical
processes, the unchanged full oracle, and all real compiler files without
starting a process:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v5.py --verify-context

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_native_source_build_v5.py --verify-context
```

The self-test must pass at least **100 distinct positive controls** and
**150 distinct hostile controls**. Its wall actively blocks filesystem
reads and writes, process creation, private temporary directories, threads,
clocks, networks, candidate imports, and native library loads, and proves
each guard was exercised. The actual-effect counters remain zero.

## Future builds are separately authorized

Only after committing and pushing the V5 freeze may a separately authorized
command select `--build`, one exact family, a fresh label, the exact SHA-256
of all three published V5 freeze files, and a separate
`--owned-source-sha256 PATH=SHA256` pin for **every** source owner of the
selected family.

Future evidence exclusively uses:

```text
native-source-build-v5-FAMILY-LABEL.json.gz
native-source-build-v5-FAMILY-LABEL-publication-receipt.json
native-source-build-v5-FAMILY-LABEL-failures.json.gz
native-source-build-v5-FAMILY-LABEL-failures-publication-receipt.json
```

A source build is not candidate activation. An older activator must not be
modified to consume V5 evidence, and no V5 output may be installed, imported,
benchmarked, or represented as qualified without a separately frozen,
committed, pushed, V5-aware activation and full correctness protocol.
