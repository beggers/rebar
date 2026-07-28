# Independent, from-scratch candidate audit

## What this gate proves

The project has four genuinely different engine families. A Python adapter, a
different setting, a wrapper, or another copy of an engine is not an additional
family.

| Family | Pattern parser | Pattern compiler | Matching engine |
| --- | --- | --- | --- |
| Python tree interpreter | Its own Python parser | Its own Python entry point and tree | Its own Python tree interpreter |
| C virtual machine | Its own Python bytecode parser | Its own Python bytecode compiler | Its own C virtual machine |
| Rust | Its own Rust parser | Its own Rust bytecode compiler | Its own Rust executor |
| Zig | Its own Zig parser | Its own Zig bytecode compiler | Its own Zig executor |

The frozen audit owns its complete path list in
tools/audit_candidate_independence_v1.py. The four semantic source lists are
pairwise disjoint. The audit computes actual SHA-256 hashes when it runs; it does
not freeze a moving source file or silently reuse an earlier hash. A caller can
require any exact source or artifact using --expect-owner-sha256 PATH=SHA256.

The exact frozen source closures are:

- Python: candidates/ast_candidate.py.
- C: candidates/vm_candidate.py and candidates/_vm_native.c.
- Rust: candidates/rust_candidate.py, candidates/rust/py_bridge.c,
  candidates/rust/src/lib.rs, candidates/rust/src/newline.rs,
  candidates/rust/src/search.rs, candidates/rust/src/stack.rs,
  candidates/rust/src/unicode_tables.rs, candidates/rust/Cargo.toml, and
  candidates/rust/Cargo.lock.
- Zig: candidates/zig_candidate.py, candidates/zig/mini_regex.zig, and
  candidates/zig/py_bridge.c.

The first-party pyproject.toml and uv.lock are shared packaging metadata, not a
shared parser, compiler, executor, or regex dependency. Both locks must contain
exactly their single first-party package. The Rust manifest and lock must have
no third-party, development, build, target-specific, workspace, replacement, or
patched dependency.

## What is checked

Python adapter source is parsed as Python syntax, not searched for misleading
text. Direct Python re and _sre imports, external regular-expression packages,
another candidate's adapter or bridge, dynamic import mechanisms, suspicious
module tables, process dispatch, environment-based test detection, and
unapproved native loaders are rejected.

Zig has one necessary native loader. It must be exactly ctypes.CDLL(path), and
path must be constructed from that adapter's own __file__ and the literal
_zig_probe.so. Its matching and compilation are separately checked against the
owned Zig bridge, owned Zig engine, and owned native symbols. This allowed loader
does not authorize arbitrary shared libraries.

The C, Rust, and Zig sources are separately tokenized with native comments and
quoted literals removed from executable identifiers. C headers, Python C-API
module import targets, Zig package imports, dynamic loaders, external matching
libraries, and cross-family native symbols are checked. In particular, the text
_sre.SRE_Scanner is a required Python-compatible scanner display name, not an
import of Python's engine; the audit explicitly tests this distinction.

The Rust bridge currently has three literal support imports: copyreg, functools,
and inspect. These imports are reported, not hidden. CPython inspect can
transitively import re. Static analysis does not establish whether a particular
support path executes Python regex operations. A separate isolated candidate
runner must therefore trap calls into Python's regex production functions and
_sre.compile and combine that result with this static gate.

## Existing local native libraries

The existing native libraries are ignored by Git; they are not committed source
artifacts and this audit does not establish that they were built from the
currently audited sources. When available, the verifier reads their bytes as
data. It never imports, maps, loads, or executes them.

| Family | Local native library | Required native dependency |
| --- | --- | --- |
| C | _vm_native.cpython-314-x86_64-linux-gnu.so | libc.so.6 |
| Rust bridge | _rust_bridge.cpython-314-x86_64-linux-gnu.so | _rust_engine.so and libc.so.6 |
| Rust engine | _rust_engine.so | ld-linux-x86-64.so.2, libc.so.6, and libgcc_s.so.1 |
| Zig bridge | _zig_bridge.cpython-314-x86_64-linux-gnu.so | _zig_probe.so and libc.so.6 |
| Zig engine | _zig_probe.so | libc.so.6 |

Both foreign-function bridges must use the exact native search path $ORIGIN.
The Zig engine must have exactly the native library name _zig_probe.so. The
verifier decodes ELF headers, bounded sections, dynamic symbols, library
dependencies, library names, and native search paths itself; no external
inspection program or candidate process is started. Missing, malformed,
cross-family, duplicate, foreign, or externally resolved native dependencies
fail the audit. Every inspected file's actual size and SHA-256 is reported.

The audit additionally pins Rust 1.95.0, its matching Cargo executable, and the
official Zig 0.16.0 executable by exact file hash. It reads those compiler files
as data; it does not run the compilers or build a candidate. A separate frozen,
offline, reproducible source-build protocol is still necessary.

## Honest status

This is a static independence gate, not a correctness qualification or final
result.

- Independent source families: 4.
- Pairwise shared semantic source files: 0.
- Actual native source-to-binary provenance: NOT ESTABLISHED.
- Reproducible clean-clone native builds: NOT ESTABLISHED.
- Runtime absence of Python or third-party regex delegation: NOT ESTABLISHED.
- Candidates passing all 31,237 frozen Python checks: NOT MEASURED.
- Native undefined behavior: NOT MEASURED.
- Expanded holdout: NOT ACCESSED.
- Speed and memory against Python: NOT MEASURED.
- Winner: NOT SELECTED.

## Reproduce the source-only gate

Run this before any actual candidate evaluation. It uses only synthetic,
in-memory positive and hostile controls. File access, process creation, clocks,
candidate imports, and native-library loads are guarded. It must also pass in an
empty environment.

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/audit_candidate_independence_v1.py --self-test

    env -i \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/audit_candidate_independence_v1.py --self-test

Publish this audit source and protocol before running the actual source and
local-binary check. After publication, use the published source and protocol
hashes:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/audit_candidate_independence_v1.py --verify \
      --source-sha256 PUBLISHED_AUDIT_SOURCE_SHA256 \
      --protocol-sha256 PUBLISHED_AUDIT_PROTOCOL_SHA256

Use --family python_ast, --family c_vm, --family rust, or --family zig for an
individual frozen family. The static gate only passes if all required local
native artifacts for that family exist; a fresh clone must build them through
the separately frozen, source-pinned build protocol first.
