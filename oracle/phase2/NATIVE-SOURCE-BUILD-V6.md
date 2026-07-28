# Six original engines and two evidence-backed build corrections

This is a frozen source-build experiment. It is not a successful build,
candidate, compatibility result, speed measurement, or permission to run a
compiler.

The objective is to build six independent Python `re` replacements from
their own first-party C, Rust, Zig, C++, Go, and Fortran matching engines.
None may wrap Python `re`, `_sre`, another candidate, Go `regexp`, C++
`<regex>`, an external regex package, or a prebuilt matching engine.

The three files frozen by this version are:

- [Native source recorder](../../tools/reproduce_owned_native_source_build_v6.py).
- This protocol.
- [Exact machine-readable source contract](native-source-build-v6.json).

## What has actually been established

The standard remains stable CPython 3.14.6 and the
[frozen, complete correctness oracle](../phase1/p0-completeness-v1.json):
13 original suites and 31,237 original case executions. There are six
independently owned source families, 25 distinct first-party semantic source
files, and 13 exactly pinned interpreter and compiler files.

There are **zero qualified replacements**. Candidate compatibility, native
safety, undefined behavior, subinterpreter behavior, speed, memory, and
performance are **NOT MEASURED**. The hidden holdout has **NOT BEEN OPENED**.
Neither source-only command imports a candidate, opens a native library,
starts a compiler or reference process, samples a clock, reads a benchmark,
or chooses a winner.

The real evidence contains **61 distinct private evidence files**:

- 51 original C, Rust, and Zig candidate-history owners: 17 per family.
- Two files for the actual V4 C++ source-build success.
- Two files for the actual V4 Go source-build failure.
- Two files for the actual V4 Fortran source-build failure.
- Two files for the actual V5 Go source-build failure.
- Two files for the actual V5 Fortran source-build failure.

Evidence-file owners are not compiler processes. V2 and V4 contain 71 real
compiler and inspection processes. The actual V5 Go failure adds 5, and the
actual V5 Fortran failure adds 26, for **102** real V2, V4, and V5
processes. The separately preserved V3 Zig build adds another 15, giving
**117** across all four build versions. Process IDs are unique only within
the run that recorded them.

The earlier measured correctness mismatches remain unchanged: C 2,094, Rust
2,042, and Zig 1,764. They are failures, not qualified replacements or new
V6 candidate executions.

## Preserve the actual Go experiment

The [V5 Go failure report](evidence/native-source-build-v5-go-phase2-v5-failures.json.gz)
has SHA-256
`ff92f5f182307b5e6e123ab883e630c6aca63f8c75318fa4ac083b1d72db6169`.
Its [separate durable receipt](evidence/native-source-build-v5-go-phase2-v5-failures-publication-receipt.json)
has SHA-256
`00a126f6c462913ad00ea9961334bbeb5aa2bfd1301d02d8f8c5d55c2e239db0`.

Five real processes ran. The isolated, exact two-file Go package and its
`-buildmode=c-shared` engine compilation succeeded. The separately compiled
Python bridge failed because the real compiler-generated header was
force-included before Python's definitions could expose `SSIZE_MAX`.

The actual 2,640-byte bridge diagnostic has SHA-256
`6477560bffdde31d9422ba4c8addbb1a733cb0becbd09b5815d51d837caf477a`.
No source phase completed. Receipt `status: PASS` authenticates publication;
`build_status: FAIL` is the real build result.

V6 freezes exactly one compiler feature macro, `-D_GNU_SOURCE`, in the
separate first-party Go bridge command. It must precede the single mandatory
`-include` of the real, fresh, phase-owned `_go_engine.h`. This is an
evidence-supported correction, **not a demonstrated V6 build success**.

Each independent Go phase must still contain exactly:

```text
reference-a/go-engine-package/engine.go
reference-a/go-engine-package/go.mod
reference-a/source/candidates/go/py_bridge.c
reference-a/native/_go_engine.so
reference-a/native/_go_engine.h
reference-a/native/_go_bridge.cpython-314-x86_64-linux-gnu.so
```

The second phase must own separate package, source, cache, output, and inode
identities. The Go package never contains `py_bridge.c` or Python headers.
The generated header is produced by the actual pinned Go compiler, checked
for all nine first-party exports, and is never handwritten, imported, or
installed. The exact pinned GCC compiles the unchanged original bridge with
`-Wall -Wextra -Werror`, the authenticated generated header, and the
adjacent owned Go engine. `GOPROXY`, `GOSUMDB`, `GOWORK`, and `GOENV`
remain off; the build uses one local first-party module and no external
packages.

## Preserve the actual Fortran experiment

The [V5 Fortran failure report](evidence/native-source-build-v5-fortran-phase2-v5-failures.json.gz)
has SHA-256
`eadf8844a1bda48d2420c7b3311ced77de9fda7ccfb806f73764550080823e53`.
Its [separate durable receipt](evidence/native-source-build-v5-fortran-phase2-v5-failures-publication-receipt.json)
has SHA-256
`f9bf0a652e9c10c949d7b5faabf261d3931681548d4f5d1af69f0accc6d742f2`.

All **26 actual compiler and ELF-inspection processes succeeded**. Both
complete phases built the original Fortran engine and its original C bridge.
The 37,424-byte bridges were byte-identical:

```text
0e4197e9b16df93f5d29333fcfda928d1d29c193c0449afb730146819229faf8
```

The two 74,624-byte engines were not:

```text
reference-a  6f005b6f1ec68658857ee2ba9c21e21d65cd4c41aa8fd608d6060712db63164a
reference-b  0d1f94c1b51e0cf6527ce742c092bffe9f0ae1207b0414bab6b5be56e9b7f092
```

The authentic GNU note listings record different build IDs:

```text
reference-a  40a5c3208328deb836a2cf72b745119444150bf0
reference-b  2fd1e7d8db83bd204cd22717868f8c40c360a62a
```

Their complete section, dynamic, and symbol listing streams agree. These
observations do **not** establish that a GNU note is the only differing raw
binary section; per-section payload digests are **NOT RECORDED**. The real
outcome remains `build_status: FAIL` because reproducibility failed after
two successfully compiled phases.

V6 freezes exactly `-Wl,--build-id=none` on the original Fortran **engine**
link command. The already identical original bridge retains its actual
`-Wl,--build-id=sha1`; its source, flags, and matching implementation are
not replaced. Both phases retain `-frandom-seed=rebar-fortran-v5`, full
source and phase-root prefix maps, all nine owned engine exports, all three
owned reverse callbacks, and complete dynamic, symbol, section, and note
forensics.

Suppressing a demonstrated changing engine build ID is an
**evidence-supported, testable hypothesis**. V6 Fortran compilation and
byte-identical reproduction are **NOT MEASURED**.

## All families remain independently owned

| Family | Original public adapter | Original matching source |
| --- | --- | --- |
| C | `candidates/vm_candidate.py` | `candidates/_vm_native.c` |
| Rust | `candidates/rust_candidate.py` | Seven owned Rust and Cargo files plus `candidates/rust/py_bridge.c` |
| Zig | `candidates/zig_candidate.py` | `candidates/zig/mini_regex.zig` and `candidates/zig/py_bridge.c` |
| C++ | `candidates/cpp_candidate.py` | `candidates/cpp/engine.hpp`, `engine.cpp`, and `py_bridge.cpp` |
| Go | `candidates/go_candidate.py` | `candidates/go/go.mod`, `engine.go`, and `py_bridge.c` |
| Fortran | `candidates/fortran_candidate.py` | `candidates/fortran/engine.f90` and `py_bridge.c` |

The existing
[six-family independence audit](CANDIDATE-INDEPENDENCE-V2.md) must still
authenticate every original source byte and reject shared parsers,
compilers, executors, external matchers, hidden native links, and wrapper
candidates. Static independence is not runtime correctness.

Every later source build requires two independently owned phases. Every
native binary retains authentic dynamic symbols, exact dependency auditing,
`readelf --sections --wide`, and `readelf --notes --wide`. The Fortran
bridge retains its genuine three callbacks. Go remains offline and retains
all nine genuine exports. Compiler warnings cannot be suppressed.

## Safe, reproducible verification

Run the strictly in-memory hostile controls:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/reproduce_owned_native_source_build_v6.py --self-test
```

Repeat with an empty process environment:

```text
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/reproduce_owned_native_source_build_v6.py --self-test
```

Both runs must block and count every attempted filesystem access, compiler,
candidate import, process, thread, clock, network, native library, and
holdout access. The controls reject missing, repeated, misplaced, or
weakened Go feature macros; foreign or guessed generated headers; wrappers;
missing Fortran seed and prefix maps; the old or repeated Fortran engine
build-ID flag; an unwanted Fortran bridge change; altered history, forged
process totals, invented completed phases, and false passing failures.

Authenticate the complete 61-owner historical context without running a
compiler:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/reproduce_owned_native_source_build_v6.py --verify-context
```

Repeat with an empty environment:

```text
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/reproduce_owned_native_source_build_v6.py --verify-context
```

Read-only verification authenticates each complete bounded historical
archive and receipt, all actual process output, both original failure
classifications, all six source families, and every exact pinned compiler
file. It performs **zero** candidate executions, compiler runs,
activations, clock samples, benchmark reads, or holdout accesses.

A future V6 build is a separately authorized experiment after this
three-file source freeze has been reviewed, committed, and pushed. It must
pin all three published file hashes, select exactly one family, use a fresh
label, and pin every independently owned family source. It may publish only
an exact new V6 success or failure archive and its independent durable
receipt. No V6 source build may be represented as candidate activation,
full-oracle correctness, a faster replacement, or a winning `rebar`.
